"""
Nodes package for PocketFlow.

This package contains all node implementations organized by functionality.
"""

from .email import (
    FetchEmailNode,
    SendEmailNode,
    ConversationContextNode
)

from .agent import (
    AgentNode,
    PopAgentActionNode
)

from .content import (
    ContentCreatorNode,
    ContentParamNode,
    GenerateContentNode
)

from .investigation import (
    InvestigateTopicNode
)

from .bitcoin import (
    PurchaseTokensWithBitcoinNode
)

from .user_status import (
    UserStatusCheckNode,
    TokenValidationNode,
    PaymentRequestNode,
    TokenConsumptionNode,
    FlowTypeRouterNode
)

from ..core.node import SimpleNode

class FinishNode(SimpleNode):
    """A simple terminal node for flow completion."""
    def process(self, shared):
        return {"route": "finish"}

__all__ = [
    # Email nodes
    "FetchEmailNode",
    "SendEmailNode", 
    "ConversationContextNode",
    
    # Agent nodes
    "AgentNode",
    "PopAgentActionNode",
    
    # Content nodes
    "ContentCreatorNode",
    "ContentParamNode",
    "GenerateContentNode",
    
    # Investigation nodes
    "InvestigateTopicNode",
    
    # Bitcoin nodes
    "PurchaseTokensWithBitcoinNode",
    
    # User status nodes
    "UserStatusCheckNode",
    "TokenValidationNode",
    "PaymentRequestNode",
    "TokenConsumptionNode",
    "FlowTypeRouterNode",
    "FinishNode",
] 