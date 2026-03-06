"""
LLM service for PocketFlow.

This module provides LLM functionality with support for multiple providers.
"""

import openai
import google.generativeai as genai
from typing import List, Dict, Any, Optional, Union
import json
import time

from ..core.types import AgentAction
from ..config.settings import get_settings, get_llm_config
from ..utils.errors import LLMError, RetryableError
from ..utils.logging import get_logger


class LLMService:
    """Service for handling LLM operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm_config = get_llm_config()
        self.logger = get_logger("LLMService")
        self._setup_providers()
    
    def _setup_providers(self):
        """Setup LLM providers based on configuration."""
        # Default to Ollama, only setup other providers if API keys are available
        if self.settings.OPENAI_API_KEY:
            openai.api_key = self.settings.OPENAI_API_KEY
            self.logger.info("OpenAI API key configured")
        if self.settings.GOOGLE_API_KEY:
            genai.configure(api_key=self.settings.GOOGLE_API_KEY)
            self.logger.info("Google API key configured")
        
        # Always log Ollama configuration
        self.logger.info(f"Using Ollama at {self.settings.OLLAMA_HOST}:{self.settings.OLLAMA_PORT}")
    
    def call_llm(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Call the LLM with the given messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters for the LLM call
            
        Returns:
            LLM response as string
            
        Raises:
            LLMError: If LLM call fails
        """
        try:
            self.logger.info(f"Calling LLM with {len(messages)} messages")
            
            # Default to Ollama, fallback to other providers if available
            try:
                return self._call_ollama(messages, **kwargs)
            except Exception as ollama_error:
                self.logger.warning(f"Ollama call failed: {ollama_error}")
                
                # Try OpenAI if API key is available
                if self.settings.OPENAI_API_KEY:
                    try:
                        return self._call_openai(messages, **kwargs)
                    except Exception as openai_error:
                        self.logger.warning(f"OpenAI call failed: {openai_error}")
                
                # Try Google if API key is available
                if self.settings.GOOGLE_API_KEY:
                    try:
                        return self._call_google(messages, **kwargs)
                    except Exception as google_error:
                        self.logger.warning(f"Google call failed: {google_error}")
                
                # If all providers fail, raise the original Ollama error
                raise LLMError(f"All LLM providers failed. Last error: {ollama_error}")
                
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise LLMError(f"LLM call failed: {e}")
    
    def _call_openai(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call OpenAI API."""
        try:
            from openai import OpenAI
            timeout = kwargs.get('timeout', self.settings.LLM_TIMEOUT)
            client = OpenAI(
                api_key=self.settings.OPENAI_API_KEY,
                timeout=timeout
            )
            response = client.chat.completions.create(
                model=self.settings.LLM_MODEL,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', self.settings.LLM_MAX_TOKENS),
                temperature=kwargs.get('temperature', self.settings.LLM_TEMPERATURE)
            )
            return response.choices[0].message.content
            
        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str or "insufficient_quota" in error_str:
                self.logger.warning("OpenAI quota exceeded, falling back to Ollama")
                return self._get_local_fallback_response(messages)
            elif "rate limit" in error_str:
                raise RetryableError(f"OpenAI rate limit: {e}")
            else:
                raise LLMError(f"OpenAI API error: {e}")
    
    def _call_ollama(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call Ollama LLM API."""
        try:
            import requests
            import json
            
            # Convert messages to a single prompt
            prompt = ""
            for msg in messages:
                role = msg.get('role', '')
                content = msg.get('content', '')
                if role == 'system':
                    prompt += f"System: {content}\n\n"
                elif role == 'user':
                    prompt += f"User: {content}\n\n"
                elif role == 'assistant':
                    prompt += f"Assistant: {content}\n\n"
            
            # Ollama API endpoint using configured settings
            ollama_url = f"http://{self.settings.OLLAMA_HOST}:{self.settings.OLLAMA_PORT}/api/generate"
            
            # Get LLM config values
            model = self.settings.OLLAMA_MODEL
            temperature = kwargs.get('temperature', self.settings.LLM_TEMPERATURE)
            max_tokens = kwargs.get('max_tokens', self.settings.LLM_MAX_TOKENS)
            # Use LLM_TIMEOUT but ensure it's at least 600 seconds for slow models
            timeout = max(self.settings.LLM_TIMEOUT, 600)
            
            # Prepare the request data
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            self.logger.info(f"Calling Ollama LLM at {ollama_url} with model {model} (timeout: {timeout}s)")
            # Use a tuple for timeout: (connect_timeout, read_timeout)
            # This allows the connection to establish quickly but gives more time for the response
            response = requests.post(ollama_url, json=data, timeout=(10, timeout))
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response from Ollama LLM')
            else:
                self.logger.warning(f"Ollama API returned status {response.status_code}")
                raise Exception(f"Ollama API error: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Ollama LLM call failed: {e}")
            raise LLMError(f"Ollama LLM call failed: {e}")

    def _call_local_llm(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call local Ollama LLM (legacy fallback method)."""
        self.logger.warning("Using legacy _call_local_llm method, consider using _call_ollama directly")
        return self._call_ollama(messages, **kwargs)
    
    def _get_local_fallback_response(self, messages: List[Dict[str, str]]) -> str:
        """Call Ollama LLM when external LLM is unavailable."""
        self.logger.info("Calling Ollama LLM as fallback")
        return self._call_ollama(messages)
    
    def _call_google(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call Google Generative AI API."""
        try:
            model = genai.GenerativeModel(self.settings.LLM_MODEL)
            
            # Convert messages to Google format
            google_messages = []
            for msg in messages:
                if msg['role'] == 'user':
                    google_messages.append(msg['content'])
                elif msg['role'] == 'assistant':
                    # For Google API, we need to handle assistant messages differently
                    # This is a simplified approach
                    pass
            
            # For now, just use the last user message
            if google_messages:
                response = model.generate_content(google_messages[-1])
                return response.text
            else:
                raise LLMError("No user messages found")
                
        except Exception as e:
            raise LLMError(f"Google API error: {e}")
    
    def extract_actions(self, response: str) -> List[AgentAction]:
        """
        Extract actions from LLM response.
        
        Args:
            response: Raw LLM response
            
        Returns:
            List of AgentAction objects
        """
        try:
            self.logger.info("Extracting actions from LLM response")
            
            # Try to extract JSON from the response
            actions = self._extract_json_actions(response)
            if actions:
                return actions
            
            # Fallback: try to parse as simple action
            action = self._parse_simple_action(response)
            if action:
                return [action]
            
            self.logger.warning("No actions found in LLM response")
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to extract actions: {e}")
            return []
    
    def _extract_json_actions(self, response: str) -> List[AgentAction]:
        """Extract actions from JSON response."""
        try:
            # Look for JSON blocks in the response
            import re
            json_match = re.search(r'```json\s*([\s\S]+?)```', response)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # Try to find JSON without code blocks
                json_match = re.search(r'\[[\s\S]*\]', response)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    return []
            
            # Parse JSON
            actions_data = json.loads(json_str)
            
            # Convert to AgentAction objects
            actions = []
            if isinstance(actions_data, list):
                for action_data in actions_data:
                    if isinstance(action_data, dict):
                        action = AgentAction(
                            action=action_data.get('action'),
                            parameters=action_data.get('parameters', {})
                        )
                        actions.append(action)
            elif isinstance(actions_data, dict):
                action = AgentAction(
                    action=actions_data.get('action'),
                    parameters=actions_data.get('parameters', {})
                )
                actions.append(action)
            
            return actions
            
        except Exception as e:
            self.logger.warning(f"Failed to extract JSON actions: {e}")
            return []
    
    def _parse_simple_action(self, response: str) -> Optional[AgentAction]:
        """Parse simple action from text response."""
        try:
            # Simple keyword-based action extraction
            response_lower = response.lower()
            
            if "generate" in response_lower:
                return AgentAction(action="generate", parameters={
                    "type": "sound",
                    "prompt": response
                })
            elif "send" in response_lower:
                return AgentAction(action="send", parameters={
                    "body": response
                })
            elif "investigate" in response_lower:
                return AgentAction(action="investigate", parameters={
                    "query": response
                })
            elif "finish" in response_lower:
                return AgentAction(action="finish", parameters={})
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to parse simple action: {e}")
            return None
    
    def generate_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Generate system prompt based on context.
        
        Args:
            context: Context information for prompt generation
            
        Returns:
            System prompt string
        """
        base_prompt = """You are an email assistant. Your job is to help users with their requests.

You can choose one of these actions:
- send: Reply to the sender or to a specified recipient.
  - to: recipient email (use {sender_email} to reply to the original sender)
  - body: email body text (REQUIRED - must not be empty)
  - attachment: full path to the generated file (e.g., /tmp/pocketflow_podcasts/podcast_1234567890.wav)
- generate: Generate content (sound, image, or document).
  - type: sound, image, or document
  - prompt: a description of what to generate
  - duration: (optional, in seconds)
- investigate: Research a topic or answer a question using web search.
- finish: End the conversation and trigger a guaranteed response to the sender.

IMPORTANT: When using the 'send' action with an attachment, you MUST use the actual file path from the tool results, not a placeholder like "<generated file>".

Reply ONLY in JSON format, and nothing else. Do NOT add any text before or after the JSON block.

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
      "to": "user@example.com",
      "body": "Here is your requested song!",
      "attachment": "{generated_file}"
    }
  },
  {
    "action": "finish",
    "parameters": {}
  }
]
```"""
        
        # Add context-specific information
        if context.get("user_has_tokens"):
            base_prompt += "\n\nNote: The user has tokens available for content generation."
        else:
            base_prompt += "\n\nNote: The user has no tokens. If they request content generation, you should request payment instead."
        
        if context.get("last_error"):
            base_prompt += f"\n\nPrevious error: {context['last_error']}"
        
        if context.get("conversation"):
            base_prompt += f"\n\nConversation history: {context['conversation']}"
        
        return base_prompt 