"""
Conversation context node for PocketFlow.

This node manages conversation context and integrates with RAG services.
"""

from typing import Dict, Any, Optional, List
from ...core.node import Node
from ...core.types import SharedState
from ...utils.logging import get_logger
from ...services.conversation_service import ConversationService

logger = get_logger("ConversationContextNode")

class ConversationContextNode(Node):
    """Node for managing conversation context and RAG integration."""
    
    def __init__(self, name: str = "conversation_context"):
        super().__init__(name)
        self.conversation_service = ConversationService()
    
    def prep(self, shared: SharedState):
        """Prepare conversation context with RAG enhancement."""
        email = shared.email
        if not email:
            logger.info("No email found, skipping conversation context")
            return "no_email"
        
        # Extract sender email
        from_field = email.get("from", "")
        sender_email = None
        if "<" in from_field and ">" in from_field:
            sender_email = from_field.split("<")[1].split(">")[0]
        else:
            sender_email = from_field
        
        if not sender_email:
            logger.error("Could not extract sender email")
            return None
        
        # Get current conversation
        conversation = shared.conversation or []
        
        # Optimize conversation memory if needed
        optimized_conversation = self.conversation_service.optimize_conversation_memory(
            conversation, sender_email
        )
        
        # Get current message content
        current_message = email.get("body", "") or email.get("subject", "")
        
        # Retrieve relevant context using RAG
        relevant_context = self.conversation_service.get_relevant_context(
            current_message=current_message,
            user_email=sender_email,
            top_k=3
        )
        
        return {
            'sender_email': sender_email,
            'optimized_conversation': optimized_conversation,
            'relevant_context': relevant_context,
            'current_message': current_message,
            'email': email
        }
    
    def exec(self, prep_result):
        """Execute conversation context processing."""
        if prep_result == "no_email":
            return "no_email"
        
        sender_email = prep_result['sender_email']
        optimized_conversation = prep_result['optimized_conversation']
        relevant_context = prep_result['relevant_context']
        current_message = prep_result['current_message']
        email = prep_result['email']
        
        # Build enhanced context
        enhanced_context = self._build_enhanced_context(
            optimized_conversation, relevant_context, current_message
        )
        
        logger.info(f"Enhanced conversation context for {sender_email}")
        return enhanced_context
    
    def post(self, shared: SharedState, prep_res, exec_res):
        """Post-process by updating shared state with enhanced context."""
        if exec_res == "no_email":
            return "finish"
        
        # Update shared state with enhanced context
        shared.conversation = exec_res.get('conversation', [])
        shared.rag_context = exec_res.get('rag_context', {})
        
        # Store conversation context for future retrieval
        if prep_res and prep_res.get('sender_email'):
            sender_email = prep_res['sender_email']
            conversation = exec_res.get('conversation', [])
            
            # Store in RAG system
            self.conversation_service.store_conversation_context(
                user_email=sender_email,
                conversation=conversation,
                metadata={
                    'email_subject': prep_res.get('email', {}).get('subject', ''),
                    'timestamp': exec_res.get('timestamp', '')
                }
            )
        
        logger.info("Updated shared state with enhanced conversation context")
        return "default"
    
    def _build_enhanced_context(self, conversation: List[Dict], relevant_context: Dict, current_message: str) -> Dict:
        """Build enhanced context using RAG information."""
        enhanced_context = {
            'conversation': conversation,
            'rag_context': relevant_context,
            'current_message': current_message,
            'timestamp': self._get_timestamp()
        }
        
        # Add context insights
        similar_conversations = relevant_context.get('similar_conversations', [])
        user_patterns = relevant_context.get('user_patterns', [])
        
        if similar_conversations:
            enhanced_context['context_insights'] = {
                'similar_conversations_count': len(similar_conversations),
                'top_similarity': similar_conversations[0].get('similarity', 0) if similar_conversations else 0,
                'has_relevant_history': True
            }
        
        if user_patterns:
            enhanced_context['user_insights'] = {
                'patterns_count': len(user_patterns),
                'pattern_types': list(set(p.get('pattern_type') for p in user_patterns))
            }
        
        return enhanced_context
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat() 