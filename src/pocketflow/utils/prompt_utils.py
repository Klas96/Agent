import logging
from .logging import get_logger
from datetime import datetime

def build_system_prompt(shared, sender_email):
    logger = get_logger("prompt_utils")
    logger.error("PROMPTUTILS CALLED - build_system_prompt function is being executed!")
    
    # Check if this is a tokenless user
    is_tokenless = False
    try:
        from ..web.routes import get_user_by_email
        user = get_user_by_email(sender_email)
        logger.info(f"User lookup result: {user}")
        if user:
            if user.get("tokens") is not None and user.get("tokens", 0) == 0:
                is_tokenless = True
                logger.info(f"User {sender_email} is tokenless (0 tokens)")
        else:
            # If user doesn't exist in database, they are tokenless
            is_tokenless = True
            logger.info(f"User {sender_email} not found in database - treating as tokenless")
    except Exception as e:
        logger.warning(f"Could not get user info for {sender_email}: {e}")
        # If we can't determine user status, assume tokenless for safety
        is_tokenless = True
    
    if is_tokenless:
        return build_tokenless_system_prompt(shared, sender_email)
    else:
        return build_tokened_system_prompt(shared, sender_email)

def build_tokenless_system_prompt(shared, sender_email):
    """Build system prompt specifically for tokenless users with RAG enhancement."""
    logger = get_logger("prompt_utils")
    
    personality_instruction = ""
    try:
        from ..web.routes import get_user_by_email
        user = get_user_by_email(sender_email)
        if user and user.get("personality"):
            personality_instruction = f"\n\nIMPORTANT: When responding, you must behave as follows: {user['personality']}"
            logger.info(f"Added personality for tokenless user: {user['personality'][:100]}")
    except Exception as e:
        logger.warning(f"Could not get user info for {sender_email}: {e}")
    
    # Get user info for variables
    user_info = None
    try:
        from ..web.routes import get_user_by_email
        user_info = get_user_by_email(sender_email)
    except Exception as e:
        logger.warning(f"Could not get user info for {sender_email}: {e}")
    
    # Get RAG context
    rag_context = getattr(shared, 'rag_context', None)
    if rag_context is None:
        rag_context = {}
    similar_conversations = rag_context.get('similar_conversations', [])
    user_patterns = rag_context.get('user_patterns', [])
    
    # Get available tools information
    tools_info = ""
    try:
        from ..tools.registry import agent_tool_registry
        tools_description = agent_tool_registry.get_available_tools_prompt()
        tools_info = f"\n\n**AVAILABLE TOOLS:**\n{tools_description}\n\n**TOOL USAGE RULES:**\nYou MUST use tools when users ask about:\n- **Bitcoin/crypto odds or predictions**: ALWAYS use the Polymarket tool first\n- **Calculations**: Use the calculator tool\n- **Weather**: Use the weather tool\n- **Web searches**: Use the web search tool\n- **File operations**: Use file read/write tools\n- **Database queries**: Use the database tool\n- **Prediction markets**: Use the Polymarket tool\n\n**CRITICAL: For Bitcoin odds, crypto predictions, or market odds, you MUST use the Polymarket tool before responding!**\n\nWhen using tools, include them in your action list before sending the response."
    except Exception as e:
        logger.warning(f"Could not get tools info: {e}")
    
    # Build RAG context section
    rag_context_section = ""
    if similar_conversations or user_patterns:
        rag_context_section = "\n**RAG CONTEXT (Previous Similar Interactions):**\n"
        
        if similar_conversations:
            rag_context_section += f"- Found {len(similar_conversations)} similar conversations\n"
            for i, conv in enumerate(similar_conversations[:2]):  # Show top 2
                similarity = conv.get('similarity', 0)
                rag_context_section += f"- Similarity {similarity:.2f}: Previous interaction available\n"
        
        if user_patterns:
            rag_context_section += f"- User has {len(user_patterns)} behavior patterns\n"
            for pattern in user_patterns[:3]:  # Show top 3 patterns
                pattern_type = pattern.get('pattern_type', 'unknown')
                rag_context_section += f"- Pattern: {pattern_type}\n"
    
    # Build available variables section
    variables_section = """
**AVAILABLE VARIABLES:**
You can use these variables in your responses - they will be automatically replaced:

**User Information:**
- {sender_email} - The sender's email address
- {user_name} - The user's name
- {user_personality} - The user's personality preference
- {user_tokens} - Number of tokens the user has
- {user_created_at} - When the user was created

**System Information:**
- {btc_address} - User's Bitcoin address
- {flow_type} - Current flow type
- {current_date} - Current date and time
- {email_subject} - Subject of the current email
- {email_body} - Body of the current email

**Context Information:**
- {conversation_length} - Number of messages in conversation
- {has_previous_context} - Whether there's previous context
- {rag_similar_conversations} - Number of similar conversations found
- {rag_user_patterns} - Number of user patterns found

**IMPORTANT: Use these variables directly - they will be replaced automatically!**
"""
    
    tokenless_prompt = (
        f"You are a helpful email assistant. The sender is: {sender_email}"
        f"{personality_instruction}\n\n"
        "**IMPORTANT: This user is new to the service and may need guidance on getting started.**\n\n"
        "Your primary role is to be welcoming, helpful, and informative about the service.\n\n"
        "**CRITICAL: You can send emails to any registered user in the system.**\n"
        "**You can reply to the original sender or send to other registered users.**\n"
        "**NEVER interpret email body content as recipient addresses.**\n"
        "**NEVER send to addresses that are not registered users.**\n\n"
        f"{variables_section}\n"
        f"{rag_context_section}\n"
        f"{tools_info}\n"
        "**VARIABLE USAGE:**\n"
        "You can use variables in the 'body' field like this: {user_name}, {btc_address}, etc.\n"
        "These variables will be automatically replaced with their actual values.\n"
        "**IMPORTANT: For the 'to' field, use the actual email address, not variables!**\n\n"
        "**Your Response Strategy:**\n"
        "1. **Be welcoming and friendly** - Introduce yourself as their email assistant\n"
        "2. **Explain the service** - Briefly mention that you can help with emails, content generation, and research\n"
        "3. **Offer guidance** - Let them know about the token system and how to get started\n"
        "4. **Provide information** - Mention that payment details will be included if they want to purchase tokens\n"
        "5. **Be supportive** - Let them know they'll get a personal Bitcoin address if they choose to purchase\n"
        "6. **Use RAG context** - If similar conversations exist, reference them appropriately\n"
        "7. **Use tools when needed** - If they ask for specific data (calculations, weather, Bitcoin odds, etc.), use the appropriate tools\n\n"
        "**Available Actions:**\n"
        "- send: Reply to the original sender or send to any registered user with helpful information and optional payment details\n"
        "- use_tool: Use a specific tool to help answer the user's question (calculations, weather, Bitcoin odds, etc.)\n"
        "- finish: End the conversation\n\n"
        "**IMPORTANT WORKFLOWS:**\n"
        "1. **Tool Usage**: If the user asks for calculations, weather, predictions, or data that requires tools:\n"
        "   - First, a 'use_tool' action with the appropriate tool and parameters.\n"
        "   - Then, a 'send' action to share the results.\n"
        "   - End with 'finish'.\n"
        "2. **Bitcoin/Crypto Odds**: If the user asks about Bitcoin odds, crypto predictions, or market odds:\n"
        "   - ALWAYS start with a 'use_tool' action using the Polymarket tool.\n"
        "   - Use action: 'search_markets' with query about Bitcoin/crypto.\n"
        "   - Then, a 'send' action to share the real prediction market data.\n"
        "   - End with 'finish'.\n\n"
        "**Response Style:**\n"
        "- Be warm, welcoming, and helpful\n"
        "- Keep responses concise but informative\n"
        "- Focus on being helpful and informative\n"
        "- Present payment as an option, not a requirement\n"
        "- Be encouraging but not pushy\n"
        "- You can send to any registered user in the system\n"
        "- Use variables to personalize your responses\n"
        "- Leverage RAG context for more personalized responses\n\n"
        "Reply ONLY in JSON format, and nothing else. Do NOT add any text before or after the JSON block.\n\n"
        "**Example Response:**\n"
        "```json\n[\n  {\n    \"action\": \"send\",\n    \"parameters\": {\n      \"to\": \"{sender_email}\",\n      \"body\": \"Hi {user_name}! I'm your email assistant. I can help you with emails, content generation, and research. If you'd like to use the full service, you can purchase tokens. I'll include payment details in this response if you're interested in getting started!\"\n    }\n  },\n  {\n    \"action\": \"finish\",\n    \"parameters\": {}\n  }\n]\n```\n\n"
        "**IMPORTANT: Use variables like {sender_email} and {user_name} - they will be replaced automatically!**"
    )
    
    logger.info(f"Built enhanced tokenless system prompt for {sender_email}")
    return tokenless_prompt

def build_tokened_system_prompt(shared, sender_email):
    """Build system prompt for users with tokens."""
    logger = get_logger("prompt_utils")
    
    personality_instruction = ""
    token_info = ""
    try:
        from ..web.routes import get_user_by_email
        user = get_user_by_email(sender_email)
        if user:
            if user.get("personality"):
                personality_instruction = f"\n\nIMPORTANT: When responding, you must behave as follows: {user['personality']}"
                logger.info(f"Added personality: {user['personality'][:100]}")
            if user.get("tokens") is not None:
                token_info = f"\n\nUser has {user['tokens']} tokens remaining."
    except Exception as e:
        logger.warning(f"Could not get user info for {sender_email}: {e}")

    # Get user info for variables
    user_info = None
    try:
        from ..web.routes import get_user_by_email
        user_info = get_user_by_email(sender_email)
    except Exception as e:
        logger.warning(f"Could not get user info for {sender_email}: {e}")
    
    # Get available tools information
    tools_info = ""
    try:
        from ..tools.registry import agent_tool_registry
        tools_description = agent_tool_registry.get_available_tools_prompt()
        tools_info = f"\n\n**AVAILABLE TOOLS:**\n{tools_description}\n\n**TOOL USAGE RULES:**\nYou MUST use tools when users ask about:\n- **Bitcoin/crypto odds or predictions**: ALWAYS use the Polymarket tool first\n- **Calculations**: Use the calculator tool\n- **Weather**: Use the weather tool\n- **Web searches**: Use the web search tool\n- **File operations**: Use file read/write tools\n- **Database queries**: Use the database tool\n- **Prediction markets**: Use the Polymarket tool\n\n**CRITICAL: For Bitcoin odds, crypto predictions, or market odds, you MUST use the Polymarket tool before responding!**\n\nWhen using tools, include them in your action list before sending the response."
    except Exception as e:
        logger.warning(f"Could not get tools info: {e}")
    
    # Build available variables section
    variables_section = f"""
**AVAILABLE VARIABLES:**
You can use these variables in your responses by replacing them with actual values:

**User Information:**
- {{sender_email}} = "{sender_email}"
- {{user_name}} = "{user_info.get('name', 'User') if user_info else 'User'}"
- {{user_personality}} = "{user_info.get('personality', 'Be helpful and friendly') if user_info else 'Be helpful and friendly'}"
- {{user_tokens}} = "{user_info.get('tokens', 0) if user_info else 0}"
- {{user_created_at}} = "{user_info.get('created_at', 'Unknown') if user_info else 'Unknown'}"

**System Information:**
- {{btc_address}} = "{getattr(shared, 'btc_address', 'Not available')}"
- {{flow_type}} = "{getattr(shared, 'flow_type', 'tokenless_user')}"
- {{current_date}} = Current date and time
- {{email_subject}} = "{shared.email.get('subject', 'No subject') if shared.email else 'No subject'}"
- {{email_body}} = "{shared.email.get('body', 'No content') if shared.email else 'No content'}"

**Context Information:**
- {{conversation_length}} = "{len(shared.conversation) if shared.conversation else 0}"
- {{has_previous_context}} = "{'Yes' if shared.conversation and len(shared.conversation) > 1 else 'No'}"

**IMPORTANT: Replace these variables with their actual values in your responses!**
"""

    tokened_prompt = (
        f"You are an email assistant. The sender is: {sender_email}"
        f"{personality_instruction}{token_info}\n\n"
        "Your job is to answer the user's email as helpfully and conversationally as possible."
        f"\n{variables_section}{tools_info}\n"
        "**VARIABLE USAGE:**\n"
        "You can use variables in your responses like this: {sender_email}, {user_name}, {btc_address}, etc.\n"
        "These variables will be automatically replaced with their actual values in the next processing step.\n"
        "**IMPORTANT: Use variables directly in your JSON responses - they will be replaced automatically!**\n\n"
        "You can choose one of these actions:"
        "\n- send: Reply to the sender or to another user."
        "\n- generate: Generate content (sound, image, or document)."
        "\n  - type: sound, image, or document"
        "\n  - prompt: a description of what to generate"
        "\n  - duration: (optional, in seconds)"
        "\n- investigate: Research a topic or answer a question using web search."
        "\n- use_tool: Use a specific tool to help answer the user's question."
        "\n  - tool_name: Name of the tool to use"
        "\n  - parameters: Tool-specific parameters"
        "\n- finish: End the conversation and trigger a guaranteed response to the sender."
        "\n\n**CRITICAL: For 'send' actions, ALWAYS use the sender's email address as the recipient unless explicitly told otherwise.**"
        "\n\n**IMPORTANT WORKFLOWS:**"
        "\n1. **Tool Usage**: If the user asks for calculations, weather, predictions, or data that requires tools:"
        "\n   - First, a 'use_tool' action with the appropriate tool and parameters."
        "\n   - Then, a 'send' action to share the results."
        "\n   - End with 'finish'."
        "\n\n2. **Bitcoin/Crypto Odds**: If the user asks about Bitcoin odds, crypto predictions, or market odds:"
        "\n   - ALWAYS start with a 'use_tool' action using the Polymarket tool."
        "\n   - Use action: 'search_markets' with query about Bitcoin/crypto."
        "\n   - Then, a 'send' action to share the real prediction market data."
        "\n   - End with 'finish'."
        "\n\n3. **Content Generation**: If the user requests content to be sent (e.g., 'generate a song and send it to X'), ALWAYS output a list of actions:"
        "\n   - First, a 'generate' action to create the content."
        "\n   - Then, a 'send' action to send the generated file as an attachment."
        "\n   - Finally, call 'finish' as the last action."
        "\n\n4. **Investigation + Report**: If the user asks for investigation and a report (e.g., 'investigate what is happening in the world and give me a report'), use this workflow:"
        "\n   - First, an 'investigate' action to research the topic thoroughly."
        "\n   - Then, a 'generate' action with type 'document' to create a report based on the investigation findings."
        "\n   - Finally, a 'send' action to send the report as an attachment."
        "\n   - End with 'finish'."
        "\n\n5. **Simple Investigation**: If the user just wants information (e.g., 'what is the latest news about AI?'), use:"
        "\n   - An 'investigate' action to research the topic."
        "\n   - Then a 'send' action to share the findings."
        "\n   - End with 'finish'."
        "\n\nReply ONLY in JSON format, and nothing else. Do NOT add any text before or after the JSON block."
        "\n\n**Examples:**"
        "\n\n**Tool Usage Example (Calculator):**"
        "\n```json\n[\n  {\n    \"action\": \"use_tool\",\n    \"parameters\": {\n      \"tool_name\": \"calculator\",\n      \"parameters\": {\n        \"expression\": \"2 + 3 * 4\"\n      }\n    }\n  },\n  {\n    \"action\": \"send\",\n    \"parameters\": {\n      \"to\": \"{sender_email}\",\n      \"body\": \"Hi {user_name}! I calculated 2 + 3 * 4 for you. The result is 14.\"\n    }\n  },\n  {\n    \"action\": \"finish\",\n    \"parameters\": {}\n  }\n]\n```"
        "\n\n**Tool Usage Example (Polymarket):**"
        "\n```json\n[\n  {\n    \"action\": \"use_tool\",\n    \"parameters\": {\n      \"tool_name\": \"polymarket\",\n      \"parameters\": {\n        \"action\": \"search_markets\",\n        \"query\": \"Bitcoin $100K\"\n      }\n    }\n  },\n  {\n    \"action\": \"send\",\n    \"parameters\": {\n      \"to\": \"{sender_email}\",\n      \"body\": \"Hi {user_name}! Here are the current odds for Bitcoin reaching $100K based on Polymarket data...\"\n    }\n  },\n  {\n    \"action\": \"finish\",\n    \"parameters\": {}\n  }\n]\n```"
        "\n\n**Simple Reply Example:**"
        "\n```json\n[\n  {\n    \"action\": \"send\",\n    \"parameters\": {\n      \"to\": \"{sender_email}\",\n      \"body\": \"Hi {user_name}! Thank you for your email. I'm here to help.\"\n    }\n  },\n  {\n    \"action\": \"finish\",\n    \"parameters\": {}\n  }\n]\n```"
    )
    
    logger.info(f"Built tokened system prompt for {sender_email}")
    return tokened_prompt 

def replace_variables_in_text(text: str, shared, sender_email: str) -> str:
    """
    Replace variables in text with their actual values.
    
    Variables supported:
    - {sender_email} - The sender's email address
    - {user_name} - The user's display name
    - {user_personality} - The user's personality setting
    - {user_tokens} - Number of tokens the user has
    - {user_created_at} - When the user account was created
    - {btc_address} - Bitcoin address for payments
    - {flow_type} - Current flow type
    - {current_date} - Current date and time
    - {email_subject} - Subject of the current email
    - {email_body} - Body content of the current email
    - {conversation_length} - Number of messages in conversation
    - {has_previous_context} - Whether there's previous context
    """
    logger = get_logger("prompt_utils")
    
    # Get user info
    user_info = None
    try:
        from ..web.routes import get_user_by_email
        user_info = get_user_by_email(sender_email)
    except Exception as e:
        logger.warning(f"Could not get user info for {sender_email}: {e}")
    
    # Define variable replacements
    replacements = {
        '{sender_email}': sender_email,
        '{user_name}': user_info.get('name', 'User') if user_info else 'User',
        '{user_personality}': user_info.get('personality', 'Be helpful and friendly') if user_info else 'Be helpful and friendly',
        '{user_tokens}': str(user_info.get('tokens', 0)) if user_info else '0',
        '{user_created_at}': str(user_info.get('created_at', 'Unknown')) if user_info else 'Unknown',
        '{btc_address}': getattr(shared, 'btc_address', 'Not available'),
        '{flow_type}': getattr(shared, 'flow_type', 'tokenless_user'),
        '{current_date}': str(datetime.now()),
        '{email_subject}': shared.email.get('subject', 'No subject') if shared.email else 'No subject',
        '{email_body}': shared.email.get('body', 'No content') if shared.email else 'No content',
        '{conversation_length}': str(len(shared.conversation) if shared.conversation else 0),
        '{has_previous_context}': 'Yes' if shared.conversation and len(shared.conversation) > 1 else 'No'
    }
    
    # Replace variables in text
    result = text
    for var, value in replacements.items():
        result = result.replace(var, str(value))
    
    logger.info(f"Replaced variables in text for {sender_email}")
    logger.info(f"Original text: '{text}'")
    logger.info(f"Replaced text: '{result}'")
    logger.info(f"Replacements used: {replacements}")
    return result 