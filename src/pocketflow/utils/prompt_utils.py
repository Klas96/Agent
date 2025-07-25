import logging
from .logging import get_logger

def build_system_prompt(shared, sender_email):
    logger = get_logger("prompt_utils")
    logger.error("PROMPTUTILS CALLED - build_system_prompt function is being executed!")
    personality_instruction = ""
    token_info = ""
    try:
        from ..web.routes import get_user_by_email
        user = get_user_by_email(sender_email)
        logger.info(f"User lookup result: {user}")
        if user:
            if user.get("personality"):
                personality_instruction = f"\n\nIMPORTANT: When responding, you must behave as follows: {user['personality']}"
                logger.info(f"Added personality: {user['personality'][:100]}")
            if user.get("tokens") is not None:
                token_info = f"\n\nUser has {user['tokens']} tokens remaining."
    except Exception as e:
        logger.warning(f"Could not get user info for {sender_email}: {e}")

    base_prompt = (
        f"You are an email assistant. The sender is: {sender_email}"
        f"{personality_instruction}{token_info}\n\n"
        "Your job is to answer the user's email as helpfully and conversationally as possible."
        "\n\nYou can choose one of these actions:"
        "\n- send: Reply to the sender or to a specified recipient."
        "\n- generate: Generate content (sound, image, or document)."
        "\n  - type: sound, image, or document"
        "\n  - prompt: a description of what to generate"
        "\n  - duration: (optional, in seconds)"
        "\n- investigate: Research a topic or answer a question using web search."
        "\n- finish: End the conversation and trigger a guaranteed response to the sender."
        "\n\n**IMPORTANT:**"
        "\nIf the user requests content to be sent (e.g., 'generate a song and send it to X'), ALWAYS output a list of actions:"
        "\n1. First, a 'generate' action to create the content."
        "\n2. Then, a 'send' action to send the generated file as an attachment."
        "\n3. When you are done, always call 'finish' as the last action."
        "\n\nReply ONLY in JSON format, and nothing else. Do NOT add any text before or after the JSON block."
        "\n\nExample:"
        "\n```json\n[\n  {\n    \"action\": \"generate\",\n    \"parameters\": {\n      \"type\": \"sound\",\n      \"prompt\": \"A 2-minute song in the style of Daft Punk\",\n      \"duration\": 120\n    }\n  },\n  {\n    \"action\": \"send\",\n    \"parameters\": {\n      \"to\": \"user@example.com\",\n      \"body\": \"Here is your requested song!\",\n      \"attachment\": \"<generated file>\"\n    }\n  },\n  {\n    \"action\": \"finish\",\n    \"parameters\": {}\n  }\n]\n```"
    )
    logger.info(f"Final system prompt: {base_prompt[:200]}...")
    return base_prompt 