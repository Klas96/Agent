"""
PocketFlow - A modular email processing and content generation system.

This package provides a complete email processing system with:
- Modular node architecture
- Service layer for external integrations
- Dynamic flow selection
- Token-based user management
"""

# Core imports
from .core.types import (
    SharedState,
    FlowType,
    EmailData,
    EmailSendRequest,
    ContentGenerationRequest,
    InvestigationRequest,
    AgentAction
)

from .core.flow import Flow, FlowBuilder, FlowRouter
from .core.node import Node, SimpleNode

# Service layer imports
from .services import (
    EmailService,
    LLMService,
    DatabaseService,
    ConversationService,
    MCPClient,
    MPCManager,
    get_mpc_manager
)

# Node imports
from .nodes import (
    # Email nodes
    FetchEmailNode,
    SendEmailNode,
    ConversationContextNode,
    
    # Agent nodes
    AgentNode,
    PopAgentActionNode,
    
    # MPC wrapper nodes (content/investigation nodes moved to MPC processes)
    MPCContentGeneratorNode,
    MPCToolExecutorNode,
    MPCInvestigatorNode,
    
    # User status nodes
    UserStatusCheckNode,
    TokenValidationNode,
    TokenConsumptionNode,
    FlowRoutingNode,
    FinishNode
)

# Flow imports
from .flows import (
    EmailProcessorFlow,
    TokenlessUserFlow,
    # ContentGenerationFlow and InvestigationFlow moved to MPC processes
)

from .flows.manager import flow_manager

# Configuration and utilities
from .config.settings import get_settings, get_config
from .utils.logging import setup_logging, get_logger
from .utils.errors import (
    PocketFlowError,
    EmailError,
    LLMError,
    ContentGenerationError,
    # BitcoinError and WebSearchError removed (functionality moved to MPC)
)

# Convenience functions
def create_flow(name: str, flow_type: FlowType, requires_tokens: bool = True) -> FlowBuilder:
    """
    Create a new flow builder.
    
    Args:
        name: Name of the flow
        flow_type: Type of flow
        requires_tokens: Whether the flow requires tokens
        
    Returns:
        FlowBuilder instance
    """
    return FlowBuilder(name, flow_type, requires_tokens)


def run_flow(flow_name: str, shared: SharedState) -> dict:
    """
    Run a specific flow by name.
    
    Args:
        flow_name: Name of the flow to run
        shared: Shared state for the flow
        
    Returns:
        Flow execution result
    """
    return flow_manager.run_flow(flow_name, shared)


def run_auto_select(shared: SharedState) -> dict:
    """
    Automatically select and run the appropriate flow.
    
    Args:
        shared: Shared state containing context
        
    Returns:
        Flow execution result
    """
    return flow_manager.run_auto_select(shared)


def get_available_flows() -> list:
    """
    Get information about all available flows.
    
    Returns:
        List of flow information dictionaries
    """
    return flow_manager.get_available_flows()


def get_flow_info(flow_name: str) -> dict:
    """
    Get information about a specific flow.
    
    Args:
        flow_name: Name of the flow
        
    Returns:
        Flow information dictionary
    """
    return flow_manager.get_flow_info(flow_name)


# Version information
__version__ = "2.0.0"
__author__ = "PocketFlow Team"
__description__ = "A modular email processing and content generation system"

# Package exports
__all__ = [
    # Core types
    "SharedState",
    "FlowType", 
    "EmailData",
    "EmailSendRequest",
    "ContentGenerationRequest",
    "InvestigationRequest",
    "AgentAction",
    
    # Core classes
    "Flow",
    "FlowBuilder",
    "FlowRouter",
    "Node",
    "SimpleNode",
    
    # Services
    "EmailService",
    "LLMService",
    "DatabaseService",
    "ConversationService",
    "MCPClient",
    "MPCManager",
    "get_mpc_manager",
    
    # Nodes
    "FetchEmailNode",
    "SendEmailNode",
    "ConversationContextNode",
    "AgentNode",
    "PopAgentActionNode",
    "MPCContentGeneratorNode",
    "MPCToolExecutorNode",
    "MPCInvestigatorNode",
    "UserStatusCheckNode",
    "TokenValidationNode",
    "TokenConsumptionNode",
    "FlowRoutingNode",
    "FinishNode",
    
    # Flows
    "EmailProcessorFlow",
    "TokenlessUserFlow",
    "flow_manager",
    
    # Configuration and utilities
    "get_settings",
    "get_config",
    "setup_logging",
    "get_logger",
    "PocketFlowError",
    "EmailError",
    "LLMError",
    "ContentGenerationError",
    
    # Convenience functions
    "create_flow",
    "run_flow",
    "run_auto_select",
    "get_available_flows",
    "get_flow_info",
    
    # Version info
    "__version__",
    "__author__",
    "__description__"
] 