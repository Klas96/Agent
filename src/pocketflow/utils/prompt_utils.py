import logging
from .logging import get_logger
from datetime import datetime

def build_system_prompt(shared, sender_email):
    logger = get_logger("prompt_utils")
    logger.error("PROMPTUTILS CALLED - build_system_prompt function is being executed!")
    
     # All users now use the same unified system since tokens are deprecated
    return build_unified_system_prompt(shared, sender_email)

def build_unified_system_prompt(shared, sender_email):
    """Build unified system prompt for all users (tokens deprecated)."""
    logger = get_logger("prompt_utils")
    
    personality_instruction = ""
    try:
        # Import the database service directly instead of going through web routes
        from ..services.database_service import DatabaseService
        db_service = DatabaseService()
        user = db_service.get_user(sender_email)
        logger.info(f"User lookup result: {user}")
        if user and user.personality:
            personality_instruction = f"\n\nIMPORTANT: When responding, you must behave as follows: {user.personality}"
            logger.info(f"Added personality for user: {user.personality[:100]}")
    except Exception as e:
        logger.warning(f"Could not get user info for {sender_email}: {e}")
    
    # Get user info for variables
    user_info = None
    try:
        from ..services.database_service import DatabaseService
        db_service = DatabaseService()
        user_info = db_service.get_user(sender_email)
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
        tools_info = f"\n\n**AVAILABLE TOOLS:**\n{tools_description}\n\n**TOOL USAGE RULES:**\nYou MUST use tools when users ask about:\n- **Calculations**: Use the calculator tool\n- **Weather**: Use the weather tool\n- **Web searches**: Use the web search tool\n- **File operations**: Use file read/write tools\n- **Database queries**: Use the database tool\n- **Podcast generation**: Use the podcastify tool for high-quality podcast creation\n\nWhen using tools, include them in your action list before sending the response."
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
- {user_created_at} - When the user was created

**System Information:**
- {flow_type} - Current flow type
- {current_date} - Current date and time
- {email_subject} - Email subject
- {email_body} - Email body content

**Context Information:**
- {conversation_length} - Number of messages in conversation
- {has_previous_context} - Whether there's previous context

**IMPORTANT: Replace these variables with their actual values in your responses!**
"""

    unified_prompt = (
        f"You are a helpful email assistant. The sender is: {sender_email}"
        f"{personality_instruction}\n\n"
        "**CRITICAL EXAMPLE - READ THIS FIRST:**\n"
        "When user asks: 'Generate a podcast about local LLMs'\n"
        "You MUST respond with:\n"
        "```json\n[\n  {\n    \"action\": \"use_tool\",\n    \"parameters\": {\n      \"tool_name\": \"podcastify\",\n      \"parameters\": {\n        \"topic\": \"Local LLMs and their applications\",\n        \"duration_minutes\": 10,\n        \"style\": \"conversational\",\n        \"target_audience\": \"general\",\n        \"voice_preference\": \"professional\",\n        \"output_format\": \"wav\"\n      }\n    }\n  },\n  {\n    \"action\": \"send\",\n    \"parameters\": {\n      \"to\": \"{sender_email}\",\n      \"body\": \"Here is your requested podcast about local LLMs!\"\n    }\n  },\n  {\n    \"action\": \"finish\",\n    \"parameters\": {}\n  }\n]\n```\n\n"
        "**Your primary role is to be welcoming, helpful, and informative about the service.**\n\n"
        "**CRITICAL: You can send emails to any registered user in the system.**\n"
        "**You can reply to the original sender or send to other registered users.**\n"
        "**NEVER interpret email body content as recipient addresses.**\n"
        "**NEVER send to addresses that are not registered users.**\n\n"
        f"{variables_section}\n"
        f"{rag_context_section}\n"
        f"{tools_info}\n"
        "**VARIABLE USAGE:**\n"
        "You can use variables in the 'body' field like this: {user_name}, etc.\n"
        "These variables will be automatically replaced with their actual values.\n"
        "**IMPORTANT: For the 'to' field, use the actual email address, not variables!**\n\n"
        "**Your Response Strategy:**\n"
        "1. **Be welcoming and friendly** - Introduce yourself as their email assistant\n"
        "2. **Explain the service** - Briefly mention that you can help with emails, content generation, and research\n"
        "3. **Be helpful** - Provide assistance with their requests\n"
        "4. **Use RAG context** - If similar conversations exist, reference them appropriately\n"
        "5. **Use tools when needed** - If they ask for specific data (calculations, weather, etc.), use the appropriate tools\n\n"
        "**Available Actions:**\n"
        "- send: Reply to the original sender or send to any registered user with helpful information\n"
        "- generate: Generate content (sound, image, or document).\n"
        "  - type: sound, image, or document\n"
        "  - prompt: a description of what to generate\n"
        "  - duration: (optional, in seconds)\n"
        "- use_tool: Use a specific tool to help answer the user's question (calculations, weather, etc.)\n"
        "- finish: End the conversation\n\n"
        "**IMPORTANT WORKFLOWS:**\n"
        "1. **Content Generation**: If the user asks to generate content (podcast, song, image, document):\n"
        "   - For podcasts: Use the 'use_tool' action with 'podcastify' tool for high-quality podcast creation\n"
        "   - For other content: Use the 'generate' action with the appropriate type and prompt.\n"
        "   - Then, a 'send' action to share the generated content.\n"
        "   - End with 'finish'.\n"
        "2. **Tool Usage**: If the user asks for calculations, weather, predictions, or data that requires tools:\n"
        "   - First, a 'use_tool' action with the appropriate tool and parameters.\n"
        "   - Then, a 'send' action to share the results.\n"
        "   - End with 'finish'.\n\n"
        "**CRITICAL: When the user asks to 'generate', 'create', or 'make' content (podcast, song, image, document), you MUST use the appropriate action first, NOT the 'send' action!**\n\n"
        "**MANDATORY RULE: If the user's email contains words like 'generate', 'create', 'make', 'podcast', 'song', 'music', 'image', 'document', you MUST respond with the appropriate action, NOT a 'send' action!**\n\n"
        "**PODCAST RULE: When users ask for podcast generation (e.g., 'make a podcast', 'generate a podcast', 'create a podcast'), you MUST use the 'use_tool' action with 'podcastify' tool, NOT the basic 'generate' action!**\n\n"
        "**CRITICAL INSTRUCTION: When users ask 'Can you generate...' or 'Could you create...', treat this as a DIRECT COMMAND to generate content, not a question. ALWAYS use the appropriate action in these cases!**\n\n"
        "**ABSOLUTE RULE: NEVER respond to content generation requests with a 'send' action. ALWAYS use 'generate' action first!**\n\n"
        "**EXAMPLES OF WHEN TO USE 'generate' ACTION:**\n"
        "- User says: 'Generate a podcast' → Use 'generate' action\n"
        "- User says: 'Create a song' → Use 'generate' action\n"
        "- User says: 'Make an image' → Use 'generate' action\n"
        "- User says: 'Can you generate a podcast?' → Use 'generate' action\n"
        "- User says: 'Could you create a song?' → Use 'generate' action\n\n"
        "**EXAMPLES OF WHEN TO USE 'send' ACTION:**\n"
        "- User asks a question: 'What is AI?' → Use 'send' action\n"
        "- User asks for help: 'Can you help me?' → Use 'send' action\n"
        "- User asks for information: 'Tell me about Bitcoin' → Use 'send' action\n\n"
        "**Response Style:**\n"
        "- Be warm, welcoming, and helpful\n"
        "- Keep responses concise but informative\n"
        "- Focus on being helpful and informative\n"
        "- Be encouraging but not pushy\n"
        "- You can send to any registered user in the system\n"
        "- Use variables to personalize your responses\n"
        "- Leverage RAG context for more personalized responses\n\n"
        "Reply ONLY in JSON format, and nothing else. Do NOT add any text before or after the JSON block.\n\n"
        "**CRITICAL JSON FORMATTING RULES:**\n"
        "1. Start with [ and end with ]\n"
        "2. Each action must be a complete JSON object with proper quotes\n"
        "3. All strings must be in double quotes\n"
        "4. No trailing commas\n"
        "5. No comments or explanatory text\n"
        "6. No incomplete JSON structures\n\n"
        "**Example Response:**\n"
        "```json\n[\n  {\n    \"action\": \"send\",\n    \"parameters\": {\n      \"to\": \"{sender_email}\",\n      \"body\": \"Hi {user_name}! I'm your email assistant. I can help you with emails, content generation, and research. How can I assist you today?\"\n    }\n  },\n  {\n    \"action\": \"finish\",\n    \"parameters\": {}\n  }\n]\n```\n\n"
        "**Content Generation Example:**\n"
        "```json\n[\n  {\n    \"action\": \"generate\",\n    \"parameters\": {\n      \"type\": \"sound\",\n      \"prompt\": \"A 2-minute podcast about artificial intelligence\",\n      \"duration\": 120\n    }\n  },\n  {\n    \"action\": \"send\",\n    \"parameters\": {\n      \"to\": \"{sender_email}\",\n      \"body\": \"Here is your requested podcast about artificial intelligence!\"\n    }\n  },\n  {\n    \"action\": \"finish\",\n    \"parameters\": {}\n  }\n]\n```\n\n"
        "**Podcast Generation Example (using podcastify tool):**\n"
        "```json\n[\n  {\n    \"action\": \"use_tool\",\n    \"parameters\": {\n      \"tool_name\": \"podcastify\",\n      \"topic\": \"Local LLMs and their applications\",\n      \"duration_minutes\": 10,\n      \"style\": \"conversational\",\n      \"target_audience\": \"general\",\n      \"voice_preference\": \"professional\",\n      \"output_format\": \"wav\"\n    }\n  },\n  {\n    \"action\": \"send\",\n    \"parameters\": {\n      \"to\": \"{sender_email}\",\n      \"body\": \"I've created a podcast about local LLMs for you! Here's your high-quality podcast episode.\",\n      \"attachment\": \"{generated_file}\"\n    }\n  },\n  {\n    \"action\": \"finish\",\n    \"parameters\": {}\n  }\n]\n```\n\n"
        "**IMPORTANT: Use variables like {sender_email} and {user_name} - they will be replaced automatically!**"
    )
    
    logger.info(f"Built unified system prompt for {sender_email}")
    return unified_prompt

def _get_generated_file_path(shared) -> str:
    """
    Get the path to the most recently generated file from tool results.
    
    Args:
        shared: Shared state object
        
    Returns:
        File path string or placeholder if no file found
    """
    try:
        # Check if there are tool results
        if hasattr(shared, 'tool_results') and shared.tool_results:
            # Look for the most recent tool result with a file path
            for result in reversed(shared.tool_results):
                if isinstance(result, dict) and 'result' in result:
                    result_data = result['result']
                    # Handle ToolResult objects
                    if hasattr(result_data, 'data') and isinstance(result_data.data, dict):
                        if 'file_path' in result_data.data:
                            return result_data.data['file_path']
                    # Handle plain dictionaries
                    elif isinstance(result_data, dict) and 'file_path' in result_data:
                        return result_data['file_path']
        
        # Fallback: check if there's a direct file path in shared state
        if hasattr(shared, 'generated_file_path') and shared.generated_file_path:
            return shared.generated_file_path
            
        # If no file found, return a placeholder that shows the expected pattern
        return "/tmp/pocketflow_podcasts/podcast_[timestamp].wav"
        
    except Exception as e:
        logger = get_logger("prompt_utils")
        logger.warning(f"Error getting generated file path: {e}")
        return "/tmp/pocketflow_podcasts/podcast_[timestamp].wav"

def replace_variables_in_text(text: str, shared, sender_email: str) -> str:
    """
    Replace variables in text with their actual values.
    
    Variables supported:
    - {sender_email} - The sender's email address
    - {user_name} - The user's display name
    - {user_personality} - The user's personality setting
    - {user_created_at} - When the user account was created
    - {btc_address} - Bitcoin address for payments
    - {flow_type} - Current flow type
    - {current_date} - Current date and time
    - {email_subject} - Subject of the current email
    - {email_body} - Body content of the current email
    - {conversation_length} - Number of messages in conversation
    - {has_previous_context} - Whether there's previous context
    - {generated_file} - Path to the most recently generated file (e.g., podcast, image)
    """
    logger = get_logger("prompt_utils")
    
    # Get user info
    user_info = None
    try:
        from ..services.database_service import DatabaseService
        db_service = DatabaseService()
        user_info = db_service.get_user(sender_email)
    except Exception as e:
        logger.warning(f"Could not get user info for {sender_email}: {e}")
    
    # Define variable replacements
    replacements = {
        '{sender_email}': sender_email,
        '{user_name}': user_info.name if user_info else 'User',
        '{user_personality}': user_info.personality if user_info else 'Be helpful and friendly',
        '{user_created_at}': str(user_info.created_at) if user_info else 'Unknown',
        '{btc_address}': getattr(shared, 'btc_address', 'Not available'),
        '{flow_type}': getattr(shared, 'flow_type', 'user'),
        '{current_date}': str(datetime.now()),
        '{email_subject}': shared.email.get('subject', 'No subject') if shared.email else 'No subject',
        '{email_body}': shared.email.get('body', 'No content') if shared.email else 'No content',
        '{conversation_length}': str(len(shared.conversation) if shared.conversation else 0),
        '{has_previous_context}': 'Yes' if shared.conversation and len(shared.conversation) > 1 else 'No',
        '{generated_file}': _get_generated_file_path(shared)
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