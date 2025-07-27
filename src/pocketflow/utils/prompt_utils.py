import logging
from .logging import get_logger

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
    """Build system prompt specifically for tokenless users."""
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
    
    tokenless_prompt = (
        f"You are a helpful email assistant. The sender is: {sender_email}"
        f"{personality_instruction}\n\n"
        "**IMPORTANT: This user is new to the service and may need guidance on getting started.**\n\n"
        "Your primary role is to be welcoming, helpful, and informative about the service.\n\n"
        "**Your Response Strategy:**\n"
        "1. **Be welcoming and friendly** - Introduce yourself as their email assistant\n"
        "2. **Explain the service** - Briefly mention that you can help with emails, content generation, and research\n"
        "3. **Offer guidance** - Let them know about the token system and how to get started\n"
        "4. **Provide information** - Mention that payment details will be included if they want to purchase tokens\n"
        "5. **Be supportive** - Let them know they'll get a personal Bitcoin address if they choose to purchase\n\n"
        "**Available Actions:**\n"
        "- send: Reply to the sender with helpful information and optional payment details\n"
        "- finish: End the conversation\n\n"
        "**Response Style:**\n"
        "- Be warm, welcoming, and helpful\n"
        "- Keep responses concise but informative\n"
        "- Focus on being helpful and informative\n"
        "- Present payment as an option, not a requirement\n"
        "- Be encouraging but not pushy\n\n"
        "Reply ONLY in JSON format, and nothing else. Do NOT add any text before or after the JSON block.\n\n"
        "**Example Response:**\n"
        "```json\n[\n  {\n    \"action\": \"send\",\n    \"parameters\": {\n      \"to\": \"{sender_email}\",\n      \"body\": \"Hi! I'm your email assistant. I can help you with emails, content generation, and research. If you'd like to use the full service, you can purchase tokens. I'll include payment details in this response if you're interested in getting started!\"\n    }\n  },\n  {\n    \"action\": \"finish\",\n    \"parameters\": {}\n  }\n]\n```"
    )
    
    logger.info(f"Built tokenless system prompt for {sender_email}")
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

    tokened_prompt = (
        f"You are an email assistant. The sender is: {sender_email}"
        f"{personality_instruction}{token_info}\n\n"
        "Your job is to answer the user's email as helpfully and conversationally as possible."
        "\n\nYou can choose one of these actions:"
        "\n- send: Reply to the sender or to another user."
        "\n- generate: Generate content (sound, image, or document)."
        "\n  - type: sound, image, or document"
        "\n  - prompt: a description of what to generate"
        "\n  - duration: (optional, in seconds)"
        "\n- investigate: Research a topic or answer a question using web search."
        "\n- finish: End the conversation and trigger a guaranteed response to the sender."
        "\n\n**CRITICAL: For 'send' actions, ALWAYS use the sender's email address as the recipient unless explicitly told otherwise.**"
        "\n\n**IMPORTANT WORKFLOWS:**"
        "\n1. **Content Generation**: If the user requests content to be sent (e.g., 'generate a song and send it to X'), ALWAYS output a list of actions:"
        "\n   - First, a 'generate' action to create the content."
        "\n   - Then, a 'send' action to send the generated file as an attachment."
        "\n   - Finally, call 'finish' as the last action."
        "\n\n2. **Investigation + Report**: If the user asks for investigation and a report (e.g., 'investigate what is happening in the world and give me a report'), use this workflow:"
        "\n   - First, an 'investigate' action to research the topic thoroughly."
        "\n   - Then, a 'generate' action with type 'document' to create a report based on the investigation findings."
        "\n   - Finally, a 'send' action to send the report as an attachment."
        "\n   - End with 'finish'."
        "\n\n3. **Simple Investigation**: If the user just wants information (e.g., 'what is the latest news about AI?'), use:"
        "\n   - An 'investigate' action to research the topic."
        "\n   - Then a 'send' action to share the findings."
        "\n   - End with 'finish'."
        "\n\nReply ONLY in JSON format, and nothing else. Do NOT add any text before or after the JSON block."
        "\n\n**Examples:**"
        "\n\n**Simple Reply Example:**"
        "\n```json\n[\n  {\n    \"action\": \"send\",\n    \"parameters\": {\n      \"to\": \"klas0holmgren@gmail.com\",\n      \"body\": \"Thank you for your email! I'm here to help.\"\n    }\n  },\n  {\n    \"action\": \"finish\",\n    \"parameters\": {}\n  }\n]\n```"
        "\n\n**Investigation + Report Example:**"
        "\n```json\n[\n  {\n    \"action\": \"investigate\",\n    \"parameters\": {\n      \"query\": \"current global economic trends and market conditions\",\n      \"depth\": \"comprehensive\"\n    }\n  },\n  {\n    \"action\": \"generate\",\n    \"parameters\": {\n      \"type\": \"document\",\n      \"prompt\": \"Create a comprehensive business report based on the investigation findings about global economic trends\",\n      \"research_based\": true\n    }\n  },\n  {\n    \"action\": \"send\",\n    \"parameters\": {\n      \"to\": \"klas0holmgren@gmail.com\",\n      \"body\": \"Here's your comprehensive report on global economic trends based on my investigation!\",\n      \"attachment\": \"<generated report file>\"\n    }\n  },\n  {\n    \"action\": \"finish\",\n    \"parameters\": {}\n  }\n]\n```"
        "\n\n**Simple Content Generation Example:**"
        "\n```json\n[\n  {\n    \"action\": \"generate\",\n    \"parameters\": {\n      \"type\": \"sound\",\n      \"prompt\": \"A 2-minute song in the style of Daft Punk\",\n      \"duration\": 120\n    }\n  },\n  {\n    \"action\": \"send\",\n    \"parameters\": {\n      \"to\": \"klas0holmgren@gmail.com\",\n      \"body\": \"Here is your requested song!\",\n      \"attachment\": \"<generated file>\"\n    }\n  },\n  {\n    \"action\": \"finish\",\n    \"parameters\": {}\n  }\n]\n```"
    )
    
    logger.info(f"Built tokened system prompt for {sender_email}")
    return tokened_prompt 