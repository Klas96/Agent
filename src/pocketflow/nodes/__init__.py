"""
Nodes package for PocketFlow.

This package contains all node implementations organized by functionality.
"""

from .email import (
    FetchEmailNode,
    SendEmailNode,
    ConversationContextNode,
    PostProcessNode
)
from .email.tokenless_send import TokenlessSendEmailNode

from .agent import (
    AgentNode,
    PopAgentActionNode
)

from .content import (
    ContentCreatorNode,
    ContentParamNode,
    GenerateContentNode,
    DocumentGeneratorNode
)

from .investigation import (
    InvestigateTopicNode
)

from .user_status import (
    UserStatusCheckNode,
    TokenValidationNode,
    TokenConsumptionNode,
    FlowRoutingNode
)

from ..core.node import SimpleNode
from ..utils.logging import get_logger

class FinishNode(SimpleNode):
    """A simple terminal node for flow completion."""
    def process(self, shared):
        """Mark email as read and finish the flow."""
        logger = get_logger("FinishNode")
        
        # Mark the email as read to prevent infinite loops
        email = getattr(shared, 'email', None)
        if email and email.get("id"):
            try:
                from ..services import email_service
                email_id = email.get("id")
                logger.info(f"Marking email {email_id} as read")
                success = email_service.mark_as_read(email_id)
                if success:
                    logger.info(f"Email {email_id} marked as read successfully")
                else:
                    logger.warning(f"Failed to mark email {email_id} as read")
            except Exception as e:
                logger.error(f"Failed to mark email as read: {e}")
        
        logger.info("Flow completed successfully")
        return {"route": "finish"}

__all__ = [
    # Email nodes
    "FetchEmailNode",
    "SendEmailNode", 
    "ConversationContextNode",
    "PostProcessNode",
    "TokenlessSendEmailNode",
    
    # Agent nodes
    "AgentNode",
    "PopAgentActionNode",
    
    # Content nodes
    "ContentCreatorNode",
    "ContentParamNode",
    "GenerateContentNode",
    "DocumentGeneratorNode",
    
    # Investigation nodes
    "InvestigateTopicNode",
    
    # User status nodes
    "UserStatusCheckNode",
    "TokenValidationNode",
    "TokenConsumptionNode",
    "FlowRoutingNode",
    "FinishNode",
] 