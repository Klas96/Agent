from pocketflow import Node
from utils.email_utils import fetch_unread, send_email, mark_as_read, load_greenlist
from utils.llm_utils import call_llm, get_model, is_local_model
from utils.websearch_utils import web_search
import yaml
import re
import time
from utils.electrum_utils import get_new_btc_address
import logging
import json
import os
logging.basicConfig(level=logging.INFO)
from utils.user_db import consume_tokens, get_tokens, add_btc_address, get_btc_addresses


def extract_email(sender):
    # Use raw string and single backslash for dot
    match = re.search(r'<([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})>', sender)
    if match:
        return match.group(1)
    # fallback: if sender is just the email
    match = re.search(r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', sender)
    return match.group(1) if match else sender

def extract_all_actions_from_json(response):
    import json, re
    # Try to extract the first JSON code block
    match = re.search(r"```json\s*([\s\S]+?)```", response)
    if match:
        json_str = match.group(1).strip()
    else:
        # Remove any leading code fence if present
        json_str = response.strip()
        if json_str.startswith("```json"):
            json_str = json_str[len("```json"):].strip()
        if json_str.startswith("```"):
            json_str = json_str[len("```"):].strip()
        if json_str.endswith("```"):
            json_str = json_str[:-3].strip()
    try:
        parsed = json.loads(json_str)
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict):
            return [parsed]
        else:
            return []
    except Exception as e:
        print(f"[extract_all_actions_from_json] JSON parse error: {e}")
        return []

# --- FetchEmailNode ---
class FetchEmailNode(Node):
    def prep(self, shared):
        logging.info("[DEBUG] FetchEmailNode.prep called")
        try:
            emails = fetch_unread()
            logging.info(f"[FetchEmailNode] Fetched {len(emails)} unread emails.")
            for e in emails:
                logging.info(f"[FetchEmailNode] Email: from={e.get('from')}, to={e.get('to')}, subject={e.get('subject')}")
            return emails
        except Exception as ex:
            logging.error(f"[FetchEmailNode] Exception in prep: {ex}")
            return []
    def exec(self, emails):
        logging.info(f"[DEBUG] FetchEmailNode.exec called with emails: {emails}")
        try:
            if not emails:
                logging.info("[FetchEmailNode] No unread emails found.")
                return None
            logging.info(f"[FetchEmailNode] Processing first unread email: from={emails[0].get('from')}, subject={emails[0].get('subject')}")
            return emails[0]
        except Exception as ex:
            logging.error(f"[FetchEmailNode] Exception in exec: {ex}")
            return None
    def post(self, shared, prep_res, exec_res):
        logging.info(f"[DEBUG] FetchEmailNode.post called with exec_res: {exec_res}")
        try:
            if exec_res is None:
                logging.info("[FetchEmailNode] No email to process in post.")
                shared["email"] = None
                return "no_email"
            # Greenlist check for sender
            from utils.user_db import is_greenlisted_email, is_greenlisted_domain
            sender = exec_res.get("from")
            sender_email = extract_email(sender).strip().lower() if sender else None
            sender_domain = sender_email.split("@")[-1] if sender_email and "@" in sender_email else None
            logging.info(f"[DEBUG] Checking greenlist for sender_email: {sender_email}, sender_domain: {sender_domain}")
            if not is_greenlisted_email(sender_email) and (not sender_domain or not is_greenlisted_domain(sender_domain)):
                logging.info(f"[FetchEmailNode] Sender {sender} not in greenlist. Skipping email.")
                shared["email"] = None
                return "no_email"
            logging.info(f"[FetchEmailNode] Accepted email from {sender} (subject: {exec_res.get('subject')}).")
            shared["email"] = exec_res
            shared['user'] = extract_email(exec_res.get('from', ''))
            mark_as_read(exec_res["id"])
            return "default"
        except Exception as ex:
            logging.error(f"[FetchEmailNode] Exception in post: {ex}")
            shared["email"] = None
            return "no_email"

class ConversationContextNode(Node):
    def prep(self, shared):
        email = shared.get("email")
        if not email:
            return None
        thread_id = email.get("thread_id")
        conversations = shared.setdefault("conversations", {})
        history = conversations.get(thread_id, [])
        # Add the new user message to the history
        history.append({"role": "user", "content": email["body"]})
        return {"thread_id": thread_id, "history": history}
    def exec(self, context):
        return context
    def post(self, shared, prep_res, exec_res):
        if not exec_res:
            shared["conversation"] = None
            return "no_context"
        thread_id = exec_res["thread_id"]
        history = exec_res["history"]
        shared["conversation"] = history
        shared["conversations"][thread_id] = history
        return "default"

class AgentNode(Node):
    def prep(self, shared):
        messages = []
        email = shared.get("email", {})
        sender = email.get("from") or shared.get("sender", "unknown")
        sender_email = extract_email(sender).strip().lower() if sender else "unknown"
        # Build system prompt
        system_prompt = f"""
You are an email assistant. The sender of the current email is: {sender_email}"
"""
        # Add conversation context if available
        if "conversation" in shared:
            conversation = shared["conversation"]
            if isinstance(conversation, list):
                conversation_str = "\n".join(str(x) for x in conversation)
            else:
                conversation_str = str(conversation)
            system_prompt += "\nHere is the conversation so far:\n" + conversation_str
        # Add latest email if available
        if "latest_email" in shared:
            system_prompt += "\nThe latest email is from the user:\n" + shared["latest_email"]
        last_file = shared.get("generated_file_path")
        if last_file:
            system_prompt += f"\nThe last generated file is: {last_file}. If you want to send it, use this exact filename as the attachment: {last_file}"
        if "last_error" in shared and shared["last_error"]:
            system_prompt += f"\nNote: The last operation failed with the following error: {shared['last_error']}"
        # Add instructions for actions
        system_prompt += """

Your job is to answer the user's email above as helpfully and conversationally as possible.

You can choose one of these actions:
- send: Reply to the sender or to a specified recipient.
- generate: Generate content (sound, image, or document).
  - type: sound, image, or document
  - prompt: a description of what to generate
  - duration: (optional, in seconds)
- investigate: Research a topic or answer a question using web search.
- finish: End the conversation and trigger a guaranteed response to the sender. Use this when you are done, or if you cannot process the request.

**IMPORTANT:**
If the user requests content to be sent (e.g., "generate a song and send it to X"), ALWAYS output a list of actions:
1. First, a 'generate' action to create the content.
2. Then, a 'send' action to send the generated file as an attachment.
3. When you are done, always call 'finish' as the last action.

Reply ONLY in this JSON format, and nothing else. Do NOT add any text before or after the JSON block.

Example:
```json
[
  {
    "action": "generate",
    "parameters": {
      "type": "sound",
      "prompt": "A 2-minute song in the style of Daft Punk",
      "duration": 120
    }
  },
  {
    "action": "send",
    "parameters": {
      "to": "nallenalle99@gmail.com",
      "cc": "klas0holmgren@gmail.com",
      "body": "Here is your requested song!",
      "attachment": "<generated file>"
    }
  },
  {
    "action": "finish",
    "parameters": {}
  }
]
```
"""
        messages.append({"role": "system", "content": system_prompt})
        history = shared.get("conversation", [])
        if not email or not history:
            return None
        prompt = f"""
You are an email assistant. The sender of the current email is: {sender_email}
Here is the conversation so far:
"""
        for msg in history:
            prompt += f"{msg['role']}: {msg['content']}\n"
        prompt += f"\nThe latest email is from the user:\n{email.get('body', '')}\n\n"
        prompt += """
Your job is to answer the user's email above as helpfully and conversationally as possible.

You can choose one of these actions:
- send: Reply to the sender or to a specified recipient.
- generate: Generate content (sound, image, or document).
  - type: sound, image, or document
  - prompt: a description of what to generate
  - duration: (optional, in seconds)
- investigate: Research a topic or answer a question using web search.
- finish: End the conversation and trigger a guaranteed response to the sender. Use this when you are done, or if you cannot process the request.

**IMPORTANT:**
If the user requests content to be sent (e.g., "generate a song and send it to X"), ALWAYS output a list of actions:
1. First, a 'generate' action to create the content.
2. Then, a 'send' action to send the generated file as an attachment.
3. When you are done, always call 'finish' as the last action.

Reply ONLY in this JSON format, and nothing else. Do NOT add any text before or after the JSON block.

Example:
```json
[
  {
    "action": "generate",
    "parameters": {
      "type": "sound",
      "prompt": "A 2-minute song in the style of Daft Punk",
      "duration": 120
    }
  },
  {
    "action": "send",
    "parameters": {
      "to": "nallenalle99@gmail.com",
      "cc": "klas0holmgren@gmail.com",
      "body": "Here is your requested song!",
      "attachment": "<generated file>"
    }
  },
  {
    "action": "finish",
    "parameters": {}
  }
]
```
"""
        messages.append({"role": "system", "content": prompt})
        return {"messages": messages, "sender_email": sender_email, "_shared": shared}

    def exec(self, prep_res):
        messages = prep_res["messages"]
        sender_email = prep_res["sender_email"]
        shared = prep_res["_shared"]
        task_type = "default"
        model_key = os.getenv("LLM_MODEL", "gpt-4o")  # Use environment variable
        if task_type in ("default", "coding"):
            if sender_email and sender_email != "unknown":
                import logging
                tokens_before = get_tokens(sender_email)
                logging.info(f"[AgentNode] Before consume_tokens: {sender_email} has {tokens_before} tokens.")
                result = consume_tokens(sender_email, amount=1)
                tokens_after = get_tokens(sender_email)
                logging.info(f"[AgentNode] consume_tokens({sender_email}, 1) returned: {result}. After: {tokens_after} tokens.")
                if not result:
                    shared["out_of_tokens"] = True
                    logging.info(f"[AgentNode] User is out of tokens. Setting out_of_tokens=True. shared['out_of_tokens'] now: {shared['out_of_tokens']}")
                    model_key = "local"
                else:
                    shared["out_of_tokens"] = False
                    model_key = os.getenv("LLM_MODEL", "gpt-4o")  # Use environment variable
        import logging
        try:
            logging.info(f"[AgentNode] Calling LLM for task_type '{task_type}' with model_key '{model_key}'...")
            # Convert messages to a single prompt string
            prompt = "\n".join([msg.get("content", "") for msg in messages])
            
            # Get user token status and flow type for LLM call
            user_has_tokens = shared.get("user_has_tokens", True)
            flow_type = shared.get("flow_type", "tokened_user")
            
            response = call_llm(
                prompt, 
                model=model_key,
                user_has_tokens=user_has_tokens,
                flow_type=flow_type
            )
            logging.info(f"[AgentNode] Raw LLM response: {response}")
        except Exception as ex:
            logging.error(f"[AgentNode] Exception during LLM call: {ex}")
            return []
        actions = extract_all_actions_from_json(response or "")
        return actions

    def post(self, shared, prep_res, exec_res):
        email = shared.get("email")
        actions = exec_res if exec_res else []
        logging.info(f"[AgentNode] post: exec_res={exec_res}, shared['action_queue']={shared.get('action_queue')}\n")
        
        # Check if user is out of tokens - process normally but add token note
        if shared.get("out_of_tokens", False):
            logging.info("[AgentNode] User is out of tokens, processing with token note")
            
            # Generate a proper response using local LLM
            user_question = shared.get("conversation", [{}])[-1].get("content", "").strip()
            if user_question:
                # Use local LLM to answer the user's question
                from utils.llm_utils import call_llm
                try:
                    original_response = call_llm(f"Answer this question in a friendly, conversational way: {user_question}")
                except Exception as e:
                    logging.error(f"[AgentNode] Failed to generate local response: {e}")
                    original_response = f"I'm a local AI assistant. Here's a simple response to your request: {user_question}"
            else:
                original_response = "I'm a local AI assistant. Here's a simple response to your request."
            
            # Get or create BTC address for the user
            email = shared.get("email", {}).get("from")
            token_note = ""
            if email:
                try:
                    btc_address = get_or_create_btc_address(shared, email)
                    shared["btc_address"] = btc_address
                    
                    # Get current BTC price to calculate token price in BTC
                    from utils.electrum_utils import get_btc_usd_price
                    btc_usd_price = get_btc_usd_price()
                    token_price_usd = 0.01  # $0.01 per token
                    
                    if btc_usd_price and btc_address and btc_address != "None":
                        token_price_btc = token_price_usd / btc_usd_price
                        tokens_10_price_btc = token_price_btc * 10
                        token_note = f"\n\n---\nNote: For advanced features like music generation, you'll need tokens. To purchase tokens, send Bitcoin to: {btc_address}\nEach token costs {token_price_btc:.8f} BTC (≈ ${token_price_usd:.2f}). You can purchase 10 tokens for approximately {tokens_10_price_btc:.8f} BTC."
                    else:
                        # No fallback address - direct users to contact admin
                        token_note = "\n\n---\nNote: For advanced features like music generation, you'll need tokens. To purchase tokens, please contact the administrator at admin@klasholmgren.se to get a Bitcoin address. Each token costs approximately $0.01 USD worth of Bitcoin."
                except Exception as e:
                    logging.error(f"[AgentNode] Failed to get BTC address: {e}")
                    token_note = "\n\n---\nNote: For advanced features like music generation, you'll need tokens. To purchase tokens, please contact the administrator at admin@klasholmgren.se to get a Bitcoin address. Each token costs approximately $0.01 USD worth of Bitcoin."
            else:
                token_note = "\n\n---\nNote: For advanced features like music generation, you'll need tokens."
            
            # Combine original response with token note
            shared["reply_body"] = original_response + token_note
            return "finish"  # Go directly to finish for simple responses
        
        # General output validation: must be a list of dicts with 'action'
        valid = (
            isinstance(actions, list) and
            all(isinstance(a, dict) and "action" in a for a in actions)
        )
        llm_retry_count = shared.get("agentnode_llm_retry_count", 0)
        max_llm_retries = 5
        if not valid:
            if llm_retry_count >= max_llm_retries:
                shared["agentnode_llm_error"] = (
                    f"Agent failed after {max_llm_retries} LLM attempts. "
                    "Please try rephrasing your request or use a different model."
                )
                logging.warning(f"[AgentNode] Max LLM retries ({max_llm_retries}) reached. Returning 'finish'.")
                return "finish"
            if llm_retry_count < max_llm_retries:
                logging.warning(f"[AgentNode] Output validation failed (attempt {llm_retry_count+1}/{max_llm_retries}), re-calling LLM...")
                shared["agentnode_llm_retry_count"] = llm_retry_count + 1
                new_llm_output = self.exec(prep_res)
                new_actions = new_llm_output if new_llm_output else []
                return self.post(shared, prep_res, new_actions)
            else:
                shared["generation_error"] = (
                    "Sorry, I could not understand or process your request after several attempts. Please rephrase or try again later."
                )
                logging.warning(f"[AgentNode] Output validation failed after {max_llm_retries} attempts. Returning 'finish'.")
                return "finish"
        shared["agentnode_llm_retry_count"] = 0
        shared["action_queue"] = actions[:]  # Put all actions in the queue
        # Remove: shared["agent_action"] = actions[0]
        if not actions:
            logging.warning("[AgentNode] post: ERROR: No valid actions parsed from LLM output! Returning 'finish'.")
            return "finish"
        # Always go to pop_action to process actions
        return "default"

# --- New: ContentSubtypeNode ---
class ContentCreatorNode(Node):
    def prep(self, shared):
        params = shared.get("agent_action", {}).get("parameters", {})
        print(f"[ContentCreatorNode] prep: params={params}")
        return {
            "type": params.get("type"),
            "prompt": params.get("prompt") or params.get("raw_prompt"),
            "duration": params.get("duration"),
        }

    def exec(self, params):
        ctype = params.get("type")
        prompt = params.get("prompt")
        duration = params.get("duration")
        # Keyword override for song/music
        if ctype == "sound" and prompt:
            if "song" in prompt.lower() or "music" in prompt.lower():
                subtype = "music"
            elif "podcast" in prompt.lower():
                subtype = "podcast"
            else:
                subtype = "unknown"
            # Infer or set default duration
            if duration is None and prompt:
                prompt_lower = prompt.lower()
                if "2-minute" in prompt_lower or "two minute" in prompt_lower:
                    duration = 120
                elif "3-minute" in prompt_lower or "three minute" in prompt_lower:
                    duration = 180
                elif "short" in prompt_lower:
                    duration = 60
                elif "long" in prompt_lower:
                    duration = 180
                else:
                    duration = 120  # default
            print(f"[ContentCreatorNode] Decided subtype: {subtype}, duration: {duration}")
            return {"subtype": subtype, "duration": duration}
        # Use recommended model for subtype selection
        model = "llama3:latest" if ctype == "sound" else "mistral:7b-instruct"
        llm_prompt = f"""
Given the following content type and user request, decide the best subtype for content generation.

Type: {ctype}
Request: {prompt}

If the user asks for a song or music, use subtype 'music'.
If the user asks for a podcast, use subtype 'podcast'.
Output only the subtype as a single word (e.g., podcast, music, report, essay, photo, drawing).
"""
        # Get user context for LLM call
        user_has_tokens = shared.get("user_has_tokens", True)
        flow_type = shared.get("flow_type", "tokened_user")
        
        llm_result = call_llm(
            llm_prompt, 
            model_key="local" if ctype == "sound" else "default",
            user_has_tokens=user_has_tokens,
            flow_type=flow_type
        )
        if not isinstance(llm_result, str):
            llm_result = str(llm_result)
        subtype = llm_result.strip().split()[0].lower() if llm_result.strip() else "unknown"
        print(f"[ContentCreatorNode] Decided subtype: {subtype}")
        return {"subtype": subtype, "duration": duration}

    def post(self, shared, prep_res, exec_res):
        print(f"[ContentCreatorNode] post: prep_res={prep_res}, exec_res={exec_res}")
        shared["chosen_subtype"] = exec_res.get("subtype")
        shared["chosen_duration"] = exec_res.get("duration")
        print(f"[ContentCreatorNode] post: returning 'default'")
        return "default"

# --- New: ContentParamNode ---
class ContentParamNode(Node):
    def prep(self, shared):
        params = shared.get("agent_action", {}).get("parameters", {})
        subtype = params.get("subtype") or shared.get("chosen_subtype")
        duration = params.get("duration") or shared.get("chosen_duration")
        print(f"[ContentParamNode] prep: params={params}, subtype={subtype}, duration={duration}")
        return {
            "type": params.get("type"),
            "subtype": subtype,
            "prompt": params.get("prompt") or params.get("raw_prompt"),
            "language": params.get("language", "en"),
            "longform": params.get("longform", False),
            "urls": params.get("urls"),
            "duration": duration,
            "_shared": shared,  # Pass shared for use in exec
        }

    def exec(self, params):
        print(f"[ContentParamNode] exec: params={params}")
        ctype = params.get("type")
        subtype = params.get("subtype")
        prompt = params.get("prompt")
        duration = params.get("duration")
        shared = params.get("_shared")
        MAX_DURATION = 15
        user_requested = duration
        if ctype == "sound" and subtype == "music":
            if duration is None or duration > MAX_DURATION:
                # Inform the user in the email body
                shared["musicgen_duration_warning"] = f"Note: The music generator can only create samples up to {MAX_DURATION} seconds. You requested {user_requested} seconds, so here is a {MAX_DURATION}-second sample."
                duration = MAX_DURATION
            from utils.generate_sound import generate_sound
            config = {"language": params.get("language", "en"), "longform": params.get("longform", False)}
            if duration:
                config["duration"] = duration
            filename = generate_sound(prompt, subtype, config=config, urls=params.get("urls"))
            print(f"[ContentParamNode] Generated sound file: {filename}")
            return filename  # Return the filename for attachment
        # For code generation
        if ctype == "code":
            # Get user context for LLM call
            user_has_tokens = shared.get("user_has_tokens", True)
            flow_type = shared.get("flow_type", "tokened_user")
            return call_llm(prompt, user_has_tokens=user_has_tokens, flow_type=flow_type)
        # For summarization, Q&A, instructions
        if ctype == "document" and subtype in ("summary", "report"):
            # Get user context for LLM call
            user_has_tokens = shared.get("user_has_tokens", True)
            flow_type = shared.get("flow_type", "tokened_user")
            return call_llm(prompt, user_has_tokens=user_has_tokens, flow_type=flow_type)
        print(f"[ContentParamNode] No function implemented for type={ctype}, subtype={subtype}")
        shared['last_error'] = f"No function implemented for type={ctype}, subtype={subtype}"
        return f"No function implemented for type={ctype}, subtype={subtype}"

    def post(self, shared, prep_res, exec_res):
        print(f"[ContentParamNode] post: prep_res={prep_res}, exec_res={exec_res}")
        if prep_res.get("type") == "sound" and prep_res.get("subtype") in ("podcast", "music", "song"):
            shared["attachment"] = exec_res
            if prep_res.get("subtype") == "podcast":
                shared["reply_body"] = "Here is your requested podcast!"
            else:
                shared["reply_body"] = "Here is your requested song!"
        else:
            shared["reply_body"] = exec_res
        # If a musicgen warning is present, add it to the outgoing email body
        if shared.get("musicgen_duration_warning"):
            if "send_body_extra" not in shared:
                shared["send_body_extra"] = ""
            shared["send_body_extra"] += "\n" + shared["musicgen_duration_warning"]
        # Do NOT pop the action queue or return the next action here!
        # Always return 'default' to return control to the AgentNode
        print(f"[ContentParamNode] post: returning 'default'")
        return "default"

class GenerateContentNode(Node):
    def prep(self, shared):
        params = shared.get("agent_action", {}).get("parameters", {})
        return {
            "type": params.get("type"),
            "subtype": params.get("subtype"),
            "prompt": params.get("prompt") or params.get("raw_prompt"),
            "language": params.get("language", "en"),
            "longform": params.get("longform", False),
            "urls": params.get("urls"),
            "duration": params.get("duration"),
            "_shared": shared,  # Pass shared for use in exec
        }

    def exec(self, params):
        shared = params.get("_shared", {})
        ctype = params.get("type")
        subtype = params.get("subtype")
        prompt = params.get("prompt")
        language = params.get("language", "en")
        longform = params.get("longform", False)
        urls = params.get("urls")
        duration = params.get("duration")
        # Choose task type for model selection
        if ctype == "code":
            task_type = "coding"
        elif ctype == "local":
            task_type = "local"
        elif ctype == "local_coding":
            task_type = "local_coding"
        else:
            task_type = "default"
        email = shared.get("email", {}).get("from")
        model_key = "default"
        if task_type in ("default", "coding"):
            if email:
                import logging
                tokens_before = get_tokens(email)
                logging.info(f"[GenerateContentNode] Before consume_tokens: {email} has {tokens_before} tokens.")
                result = consume_tokens(email, amount=1)
                tokens_after = get_tokens(email)
                logging.info(f"[GenerateContentNode] consume_tokens({email}, 1) returned: {result}. After: {tokens_after} tokens.")
                if not result:
                    shared["out_of_tokens"] = True
                    logging.info("[GenerateContentNode] User is out of tokens. Setting out_of_tokens=True. Falling back to local model.")
                    model_key = "local"
                else:
                    shared["out_of_tokens"] = False
                    model_key = "default"
        if ctype == "sound" and subtype == "podcast":
            from utils.generate_sound import generate_sound
            config = {"language": language, "longform": longform}
            if duration:
                config["duration"] = duration
            if urls:
                return generate_sound(prompt, subtype, config=config, urls=urls)
            elif prompt:
                return generate_sound(prompt, subtype, config=config)
            else:
                return "Missing topic or urls for podcast generation."
        # --- Updated logic for sound/song ---
        if ctype == "sound" or subtype == "song":
            from utils.generate_sound import generate_sound
            filename = generate_sound(prompt, subtype)
            return filename  # Return the filename for attachment
        # Stub: Replace with real API calls as needed
        if ctype == "image":
            return f"[Image generated: {subtype or 'generic'}] {prompt}"
        elif ctype == "sound":
            return f"[Sound generated: {subtype or 'generic'}] {prompt}"
        elif ctype == "document":
            return f"[Document generated: {subtype or 'generic'}] {prompt}"
        elif ctype == "code":
            return call_llm(prompt, model_key=model_key)
        elif ctype == "local":
            return call_llm(prompt, model_key=model_key)
        elif ctype == "local_coding":
            return call_llm(prompt, model_key=model_key)
        else:
            return f"Unknown content type: {ctype}"

    def post(self, shared, prep_res, exec_res):
        # Assume exec_res is a dict with 'file_path' if successful
        if not exec_res or not exec_res.get("file_path"):
            shared["generation_error"] = (
                "Sorry, your content could not be generated. Please check your request or try again later."
            )
            return "generation_failed"
        shared["attachment"] = exec_res["file_path"]
        return "default"

class InvestigateTopicNode(Node):
    def prep(self, shared):
        pass
    def exec(self, query):
        pass
    def post(self, shared, prep_res, exec_res):
        pass

# --- SendEmailNode ---
class SendEmailNode(Node):
    def prep(self, shared):
        logging.info(f"[DEBUG] SendEmailNode.prep called with shared['agent_action']: {shared.get('agent_action')}")
        agent_action = shared.get('agent_action', {})
        params = agent_action.get('parameters', {})
        email = shared.get('email', {})
        # Threading logic: use message_id if available, else thread_id
        in_reply_to = email.get('message_id') or email.get('thread_id')
        references = email.get('references') or in_reply_to
        # Determine recipient
        to = params.get('to')
        if not to:
            to = shared.get('user') or extract_email(email.get('from', ''))
        # Determine subject
        subject = params.get('subject')
        if subject is None:
            subject = email.get('subject', '')
        if subject and not subject.lower().startswith('re:'):
            subject = f"Re: {subject}"
        
        # Get attachment from shared state or parameters
        attachment = shared.get('attachment') or params.get('attachment')
        
        email_data = {
            'to': to,
            'subject': subject,
            'body': params.get('body'),
            'user_email': shared.get('user'),
            'in_reply_to': in_reply_to,
            'references': references,
            'attachment': attachment,
            'cc': params.get('cc'),
        }
        return email_data
    
    def exec(self, prep_res):
        logging.info(f"[DEBUG] SendEmailNode.exec called with email_data: {prep_res}")
        print(f"[DEBUG TEST] SendEmailNode.exec received email_data: {prep_res}")
        body = prep_res.get("body")
        if not body or not isinstance(body, str) or not body.strip():
            body = "Sorry, there was an error generating your reply."
        
        from utils.email_utils import send_email
        send_email(
            prep_res["to"],
            prep_res["subject"],
            body,
            attachment_path=prep_res.get("attachment"),  # Pass attachment
            cc=prep_res.get("cc"),  # Pass CC
            in_reply_to=prep_res.get("in_reply_to"),
            references=prep_res.get("references")
        )
        return True
    
    def post(self, shared, prep_res, exec_res):
        logging.info(f"[DEBUG] SendEmailNode.post called with exec_res: {exec_res}")
        if shared is not None:
            shared["sender_have_gotten_response"] = True
        return "default"

# --- PostProcessNode ---
class PostProcessNode(Node):
    def prep(self, shared):
        logging.info(f"[DEBUG] PostProcessNode.prep called with shared: {shared}")
        if shared.get("sender_have_gotten_response") is True:
            logging.info("[DEBUG] PostProcessNode.prep: sender_have_gotten_response is True, skipping.")
            return None
        email = shared.get("email")
        if not email:
            logging.info("[DEBUG] PostProcessNode.prep: No email found, skipping.")
            return None
        user_email = shared.get("user", "")
        if not user_email:
            user_email = extract_email(email.get("from", ""))
        result = dict(email)
        result["out_of_tokens"] = shared.get("out_of_tokens", False)
        result["btc_address"] = shared.get("btc_address")
        result["user_email"] = user_email
        result["reply_body"] = shared.get("reply_body", "")
        result["attachment"] = shared.get("attachment")  # Add attachment support
        return result
    
    def exec(self, prep_res):
        logging.info(f"[DEBUG] PostProcessNode.exec called with data: {prep_res}")
        if prep_res is None:
            logging.info("[DEBUG] PostProcessNode.exec: No data, returning None.")
            return None
        from utils.email_utils import send_email
        # Use the sender's email as the recipient for the reply
        recipient = prep_res.get("user_email") or prep_res.get("from")
        if not recipient:
            logging.error("[PostProcessNode] No recipient email found!")
            return None
            
        # Set up proper reply headers
        in_reply_to = prep_res.get("message_id") or prep_res.get("in_reply_to")
        references = prep_res.get("message_id") or prep_res.get("references")
        
        send_email(
            recipient,
            f"Re: {prep_res['subject']}",
            prep_res.get("reply_body", ""),
            attachment_path=prep_res.get("attachment"),  # Pass attachment
            in_reply_to=in_reply_to,
            references=references
        )
        return True
    
    def post(self, shared, prep_res, exec_res):
        logging.info(f"[DEBUG] PostProcessNode.post called with exec_res: {exec_res}")
        if exec_res:
            shared["sender_have_gotten_response"] = True
        # Remove sender_have_gotten_response key after processing for next cycle
        if "sender_have_gotten_response" in shared:
            del shared["sender_have_gotten_response"]
        logging.info("[PostProcessNode] Removed sender_have_gotten_response for next cycle.")
        return "default"

class PopAgentActionNode(Node):
    def prep(self, shared):
        queue = shared.get("action_queue", [])
        if not queue:
            print("[PopAgentActionNode] No more actions in queue.")
            return None
        action = queue.pop(0)
        shared["action_queue"] = queue
        shared["agent_action"] = action
        print(f"[PopAgentActionNode] Popped action: {action}")
        return action

    def exec(self, action):
        return action

    def post(self, shared, prep_res, exec_res):
        # exec_res is the action dict just popped
        if not exec_res or not isinstance(exec_res, dict) or 'action' not in exec_res:
            print("[PopAgentActionNode] ERROR: No valid action to route.")
            return "default"
        action_type = exec_res['action']
        print(f"[PopAgentActionNode] post: returning action '{action_type}' for routing.")
        import logging
        logging.info(f"[PopAgentActionNode] Set agent_action: {shared.get('agent_action')}")
        return action_type 

def get_or_create_btc_address(shared, email):
    import logging
    if shared is None:
        shared = {}
    btc_addresses = get_btc_addresses(email)
    if btc_addresses:
        logging.debug(f"[get_or_create_btc_address] Found existing BTC address for {email}: {btc_addresses[-1]}")
        return btc_addresses[-1]  # Return the most recent address
    
    logging.debug(f"[get_or_create_btc_address] No BTC address found for {email}, using admin addresses.")
    
    # If no addresses found for this user, use addresses from admin user
    admin_addresses = get_btc_addresses("admin@klasholmgren.se")
    if admin_addresses:
        # Assign one of the admin addresses to this user
        import random
        selected_address = random.choice(admin_addresses)
        add_btc_address(email, selected_address)
        logging.debug(f"[get_or_create_btc_address] Assigned admin BTC address for {email}: {selected_address}")
        return selected_address
    
    # Fallback: try to generate new address
    new_address = get_new_btc_address()
    if new_address and new_address != "None":
        add_btc_address(email, new_address)
        logging.debug(f"[get_or_create_btc_address] Created new BTC address for {email}: {new_address}")
        return new_address
    else:
        # No fallback address - return None when Electrum is not working
        logging.warning(f"[get_or_create_btc_address] Electrum not working, no BTC address available for {email}")
        return None

class PurchaseTokensWithBitcoinNode(Node):
    LLM_CALL_PRICE_USD = 0.01  # 1 token = $0.01 (matches LLM call price)
    DEFAULT_NUM_TOKENS = 10

    def prep(self, shared):
        email = shared.get("email", {}).get("from")
        btc_address = get_or_create_btc_address(shared, email)
        num_tokens = self.DEFAULT_NUM_TOKENS
        from utils.electrum_utils import get_btc_usd_price
        btc_usd_price = get_btc_usd_price()
        btc_per_token = self.LLM_CALL_PRICE_USD / btc_usd_price
        amount_btc = btc_per_token * num_tokens
        return {
            "email": email,
            "btc_address": btc_address,
            "amount_btc": amount_btc,
            "num_tokens": num_tokens,
            "btc_usd_price": btc_usd_price,
            "usd_per_token": self.LLM_CALL_PRICE_USD,
        }

    def exec(self, params):
        instructions = (
            f"To buy {params['num_tokens']} tokens, send {params['amount_btc']:.8f} BTC "
            f"(≈ ${params['num_tokens'] * params['usd_per_token']:.2f}) to your personal address: {params['btc_address']}.\n"
            f"Current BTC/USD price: ${params['btc_usd_price']:.2f} (1 token = ${params['usd_per_token']:.4f})\n"
            "Once payment is received, your tokens will be credited automatically."
        )
        return instructions

    def post(self, shared, prep_res, exec_res):
        shared["reply_body"] = exec_res
        return "send" 