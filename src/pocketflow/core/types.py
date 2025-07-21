"""
Core type definitions for PocketFlow.

This module defines the fundamental data structures used throughout the system.
"""

from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class NodeResult(BaseModel):
    """Result of a node execution."""
    success: bool = Field(description="Whether the node executed successfully")
    data: Optional[Any] = Field(default=None, description="Result data from the node")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SharedState(BaseModel):
    """Shared state passed between nodes in a flow."""
    email: Optional[Dict[str, Any]] = Field(default=None, description="Current email being processed")
    user: Optional[str] = Field(default=None, description="User email address")
    conversation: Optional[List[Dict[str, Any]]] = Field(default=None, description="Conversation history")
    conversations: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict, description="All conversations by thread")
    generated_file_path: Optional[str] = Field(default=None, description="Path to last generated file")
    last_error: Optional[str] = Field(default=None, description="Last error message")
    tokens_remaining: Optional[int] = Field(default=None, description="Remaining tokens for user")
    btc_address: Optional[str] = Field(default=None, description="User's Bitcoin address")
    user_has_tokens: Optional[bool] = Field(default=None, description="Whether user has tokens")
    flow_type: Optional[str] = Field(default=None, description="Type of flow being executed")
    
    class Config:
        arbitrary_types_allowed = True


class ActionType(str, Enum):
    """Types of actions that can be performed by the agent."""
    GENERATE = "generate"
    SEND = "send"
    INVESTIGATE = "investigate"
    FINISH = "finish"
    REQUEST_PAYMENT = "request_payment"  # New action for tokenless users


class ContentType(str, Enum):
    """Types of content that can be generated."""
    SOUND = "sound"
    IMAGE = "image"
    DOCUMENT = "document"
    PODCAST = "podcast"
    SONG = "song"


class FlowType(str, Enum):
    """Types of flows based on user token status."""
    TOKENED_USER = "tokened_user"      # User has tokens, full functionality
    TOKENLESS_USER = "tokenless_user"  # User has no tokens, limited functionality
    PAYMENT_PENDING = "payment_pending"  # User requested payment, waiting for confirmation


class AgentAction(BaseModel):
    """An action to be performed by the agent."""
    action: ActionType = Field(description="Type of action to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")


class EmailData(BaseModel):
    """Email data structure."""
    id: str = Field(description="Email ID")
    thread_id: str = Field(description="Thread ID")
    from_: str = Field(alias="from", description="Sender email")
    to: str = Field(description="Recipient email")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body")
    received_at: datetime = Field(description="When email was received")
    
    class Config:
        allow_population_by_field_name = True


class ContentGenerationRequest(BaseModel):
    """Request for content generation."""
    content_type: ContentType = Field(description="Type of content to generate")
    prompt: str = Field(description="Generation prompt")
    duration: Optional[int] = Field(default=None, description="Duration in seconds (for audio)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters")


class EmailSendRequest(BaseModel):
    """Request to send an email."""
    to: str = Field(description="Recipient email")
    cc: Optional[str] = Field(default=None, description="CC recipients")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body")
    attachment: Optional[str] = Field(default=None, description="Attachment file path")


class InvestigationRequest(BaseModel):
    """Request for topic investigation."""
    query: str = Field(description="Search query")
    max_results: int = Field(default=5, description="Maximum number of results")


class PaymentRequest(BaseModel):
    """Request for Bitcoin payment."""
    amount_usd: float = Field(description="Amount in USD")
    user_email: str = Field(description="User email address")
    btc_address: str = Field(description="Bitcoin address for payment")
    description: str = Field(description="Payment description")


class FlowConfig(BaseModel):
    """Configuration for a flow."""
    name: str = Field(description="Flow name")
    description: Optional[str] = Field(default=None, description="Flow description")
    nodes: List[str] = Field(description="List of node names in order")
    routing: Dict[str, Dict[str, str]] = Field(default_factory=dict, description="Routing rules")
    timeout: Optional[int] = Field(default=None, description="Flow timeout in seconds")
    flow_type: FlowType = Field(description="Type of flow")
    requires_tokens: bool = Field(description="Whether this flow requires tokens")
    
    class Config:
        extra = "forbid" 