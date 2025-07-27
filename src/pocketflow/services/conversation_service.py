"""
Conversation management service for PocketFlow RAG system.

This service handles conversation summarization, context management, and memory optimization.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..utils.logging import get_logger
from .vector_service import VectorService

logger = get_logger("ConversationService")

class ConversationService:
    """Service for managing conversation context and summarization."""
    
    def __init__(self):
        self.vector_service = VectorService()
    
    def summarize_conversation(self, conversation: List[Dict], max_length: int = 1000) -> str:
        """
        Summarize a conversation using LLM.
        In production, use a proper LLM for summarization.
        """
        if not conversation:
            return "No conversation history."
        
        # Simple summarization for demo
        # In production, use LLM for proper summarization
        summary_parts = []
        
        for msg in conversation[-5:]:  # Last 5 messages
            if isinstance(msg, dict):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                if content:
                    summary_parts.append(f"{role}: {content[:200]}...")
        
        summary = " | ".join(summary_parts)
        
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    
    def should_summarize(self, conversation: List[Dict], max_messages: int = 10) -> bool:
        """Determine if conversation should be summarized."""
        return len(conversation) > max_messages
    
    def optimize_conversation_memory(self, conversation: List[Dict], user_email: str) -> List[Dict]:
        """
        Optimize conversation memory by summarizing old messages.
        """
        if not self.should_summarize(conversation):
            return conversation
        
        # Keep recent messages (last 5)
        recent_messages = conversation[-5:]
        
        # Summarize older messages
        older_messages = conversation[:-5]
        if older_messages:
            summary = self.summarize_conversation(older_messages)
            
            # Create summary message
            summary_message = {
                'role': 'system',
                'content': f"Previous conversation summary: {summary}",
                'timestamp': datetime.now().isoformat(),
                'type': 'summary'
            }
            
            # Store in vector database
            self.vector_service.store_conversation(
                user_email=user_email,
                conversation=older_messages,
                metadata={'type': 'summarized', 'original_length': len(older_messages)}
            )
            
            # Return summary + recent messages
            return [summary_message] + recent_messages
        
        return recent_messages
    
    def get_relevant_context(self, current_message: str, user_email: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve relevant context from past conversations.
        """
        try:
            # Find similar conversations
            similar_conversations = self.vector_service.find_similar_conversations(
                query=current_message,
                user_email=user_email,
                top_k=top_k
            )
            
            # Get user patterns
            user_patterns = self.vector_service.get_user_patterns(user_email)
            
            context = {
                'similar_conversations': similar_conversations,
                'user_patterns': user_patterns,
                'retrieved_at': datetime.now().isoformat()
            }
            
            logger.info(f"Retrieved context for {user_email}: {len(similar_conversations)} similar conversations")
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return {'similar_conversations': [], 'user_patterns': [], 'retrieved_at': datetime.now().isoformat()}
    
    def store_conversation_context(self, user_email: str, conversation: List[Dict], metadata: Dict = None):
        """
        Store conversation context for future retrieval.
        """
        try:
            # Store in vector database
            self.vector_service.store_conversation(
                user_email=user_email,
                conversation=conversation,
                metadata=metadata
            )
            
            # Extract and store user patterns
            self._extract_user_patterns(user_email, conversation)
            
            logger.info(f"Stored conversation context for {user_email}")
            
        except Exception as e:
            logger.error(f"Error storing conversation context: {e}")
    
    def _extract_user_patterns(self, user_email: str, conversation: List[Dict]):
        """
        Extract user behavior patterns from conversation.
        """
        try:
            patterns = {
                'response_style': self._analyze_response_style(conversation),
                'topics': self._extract_topics(conversation),
                'preferences': self._extract_preferences(conversation)
            }
            
            for pattern_type, pattern_data in patterns.items():
                if pattern_data:
                    self.vector_service.store_user_pattern(
                        user_email=user_email,
                        pattern_type=pattern_type,
                        pattern_data=pattern_data
                    )
            
        except Exception as e:
            logger.error(f"Error extracting user patterns: {e}")
    
    def _analyze_response_style(self, conversation: List[Dict]) -> Dict:
        """Analyze user's response style."""
        if not conversation:
            return {}
        
        # Simple analysis for demo
        # In production, use more sophisticated NLP
        user_messages = [msg for msg in conversation if msg.get('role') == 'user']
        
        if not user_messages:
            return {}
        
        avg_length = sum(len(msg.get('content', '')) for msg in user_messages) / len(user_messages)
        
        return {
            'average_message_length': avg_length,
            'message_count': len(user_messages),
            'style': 'detailed' if avg_length > 100 else 'concise'
        }
    
    def _extract_topics(self, conversation: List[Dict]) -> List[str]:
        """Extract main topics from conversation."""
        # Simple topic extraction for demo
        # In production, use NLP topic modeling
        topics = []
        
        for msg in conversation:
            content = msg.get('content', '').lower()
            
            # Simple keyword-based topic extraction
            if 'token' in content or 'payment' in content:
                topics.append('payment')
            if 'email' in content or 'assistant' in content:
                topics.append('service_usage')
            if 'bitcoin' in content or 'btc' in content:
                topics.append('cryptocurrency')
        
        return list(set(topics))
    
    def _extract_preferences(self, conversation: List[Dict]) -> Dict:
        """Extract user preferences from conversation."""
        preferences = {}
        
        for msg in conversation:
            content = msg.get('content', '').lower()
            
            # Extract preferences based on content
            if 'detailed' in content or 'comprehensive' in content:
                preferences['detail_level'] = 'detailed'
            elif 'brief' in content or 'short' in content:
                preferences['detail_level'] = 'brief'
            
            if 'formal' in content:
                preferences['tone'] = 'formal'
            elif 'casual' in content or 'friendly' in content:
                preferences['tone'] = 'casual'
        
        return preferences 