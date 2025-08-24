"""
Node system for PocketFlow.

This module provides the original PocketFlow nodes and adds n8n-like workflow capabilities.
"""
from typing import Dict, List, Type

# Original PocketFlow nodes
from .email.fetch import FetchEmailNode
from .email.send import SendEmailNode
from .email.context import ConversationContextNode
from .email.postprocess import PostProcessNode
from .email.tokenless_send import TokenlessSendEmailNode
from .email.tokenless_response import TokenlessResponseNode

from .agent.core import AgentNode
from .agent.tool_agent import ToolAgentNode

from .content.generator import ContentGeneratorNode
from .content.creator import ContentCreatorNode
from .content.document_generator import DocumentGeneratorNode

from .investigation.investigation import InvestigationNode as OriginalInvestigationNode
from .investigation.topic_investigation import TopicInvestigationNode

from .user_status import UserStatusNode
from .user_status_simplified import UserStatusSimplifiedNode

# n8n-like workflow nodes (built on top of original PocketFlow)
from .workflow.base import WorkflowNode, WorkflowNodeMetadata
from .workflow.triggers import EmailFetchingNode, ScheduledTriggerNode, ManualTriggerNode
from .workflow.agents import (
    DecisionAgentNode, ContentCreatorNode, InvestigationNode, 
    MessageSendingNode, PostProcessingNode
)
from .workflow.actions import (
    SendEmailWorkflowNode, GenerateContentWorkflowNode, 
    GenerateLatexWorkflowNode, WebSearchWorkflowNode, HttpRequestWorkflowNode
)
from .workflow.conditions import IfElseWorkflowNode, TransformWorkflowNode, DelayWorkflowNode, LogWorkflowNode

# Workflow registry for n8n-like features
from .workflow.registry import WorkflowNodeRegistry

# Export original nodes for backward compatibility
__all__ = [
    # Original email nodes
    'FetchEmailNode', 'SendEmailNode', 'ConversationContextNode', 'PostProcessNode',
    'TokenlessSendEmailNode', 'TokenlessResponseNode',
    
    # Original agent nodes
    'AgentNode', 'ToolAgentNode',
    
    # Original content nodes
    'ContentGeneratorNode', 'ContentCreatorNode', 'DocumentGeneratorNode',
    
    # Original investigation nodes
    'OriginalInvestigationNode', 'TopicInvestigationNode',
    
    # Original user status nodes
    'UserStatusNode', 'UserStatusSimplifiedNode',
    
    # n8n-like workflow nodes
    'WorkflowNode', 'WorkflowNodeMetadata',
    'EmailFetchingNode', 'ScheduledTriggerNode', 'ManualTriggerNode',
    'DecisionAgentNode', 'ContentCreatorNode', 'InvestigationNode', 
    'MessageSendingNode', 'PostProcessingNode',
    'SendEmailWorkflowNode', 'GenerateContentWorkflowNode', 
    'GenerateLatexWorkflowNode', 'WebSearchWorkflowNode', 'HttpRequestWorkflowNode',
    'IfElseWorkflowNode', 'TransformWorkflowNode', 'DelayWorkflowNode', 'LogWorkflowNode',
    
    # Workflow registry
    'WorkflowNodeRegistry',
    'workflow_node_registry'
]

# Create global workflow registry instance
workflow_node_registry = WorkflowNodeRegistry() 