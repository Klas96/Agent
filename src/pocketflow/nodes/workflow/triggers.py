"""
Trigger nodes for workflow system.
These nodes inherit from the original PocketFlow Node system.
"""

from typing import Dict, Any
from ...core.node import Node
from ...core.types import SharedState
from ...services import email_service
from ...config.settings import get_settings
from ...utils.logging import get_logger
from .base import WorkflowTriggerNode, WorkflowNodeMetadata, WorkflowNodeInput, WorkflowNodeOutput


class EmailFetchingNode(WorkflowTriggerNode):
    """
    Email fetching node that monitors for new emails and triggers workflows.
    This node fetches emails and provides email data to subsequent nodes.
    """
    
    def __init__(self, config: Dict[str, Any], name: str = None):
        super().__init__(config, name)
        self.settings = get_settings()
        self.last_check = None
        
    def execute_workflow(self, config: Dict[str, Any], shared: SharedState) -> Dict[str, Any]:
        try:
            host = self.get_input_value("host", self.settings.EMAIL_HOST)
            port = self.get_input_value("port", self.settings.EMAIL_PORT)
            username = self.get_input_value("username", self.settings.EMAIL_USERNAME)
            password = self.get_input_value("password", self.settings.EMAIL_PASSWORD)
            use_tls = self.get_input_value("use_tls", True)
            
            # Fetch emails using the original PocketFlow email service
            emails = email_service.fetch_emails(
                host=host, port=port, username=username, password=password, use_tls=use_tls
            )
            
            if emails:
                email_data = emails[0] if isinstance(emails, list) else emails
                shared["email_data"] = email_data
                shared["email_subject"] = email_data.get("subject", "")
                shared["email_sender"] = email_data.get("from", "")
                shared["email_body"] = email_data.get("body", "")
                shared["email_attachments"] = email_data.get("attachments", [])
                
                return {
                    "triggered": True,
                    "email_data": email_data,
                    "subject": email_data.get("subject", ""),
                    "sender": email_data.get("from", ""),
                    "body": email_data.get("body", ""),
                    "attachments": email_data.get("attachments", []),
                    "timestamp": self._get_timestamp()
                }
            else:
                return {"triggered": False, "message": "No new emails found"}
        except Exception as e:
            self.logger.error(f"Error in email fetching: {e}")
            return {"triggered": False, "error": str(e)}
    
    @classmethod
    def get_metadata(cls) -> WorkflowNodeMetadata:
        return WorkflowNodeMetadata(
            name="EmailFetchingNode",
            description="Fetches new emails and triggers workflow execution",
            category="trigger",
            inputs=[
                WorkflowNodeInput("host", "string", "SMTP host", False),
                WorkflowNodeInput("port", "number", "SMTP port", False),
                WorkflowNodeInput("username", "string", "Email username", False),
                WorkflowNodeInput("password", "string", "Email password", False),
                WorkflowNodeInput("use_tls", "boolean", "Use TLS", False, True)
            ],
            outputs=[
                WorkflowNodeOutput("email_data", "object", "Complete email data"),
                WorkflowNodeOutput("subject", "string", "Email subject"),
                WorkflowNodeOutput("sender", "string", "Email sender"),
                WorkflowNodeOutput("body", "string", "Email body"),
                WorkflowNodeOutput("attachments", "array", "Email attachments"),
                WorkflowNodeOutput("triggered", "boolean", "Whether trigger was activated")
            ],
            icon="email",
            color="#4CAF50"
        )


class ScheduledTriggerNode(WorkflowTriggerNode):
    """
    Scheduled trigger node for time-based workflow execution.
    """
    
    def execute_workflow(self, config: Dict[str, Any], shared: SharedState) -> Dict[str, Any]:
        # For now, this is a simple implementation
        # In production, this would integrate with a proper scheduler
        schedule_type = self.get_input_value("schedule_type", "daily")
        time = self.get_input_value("time", "09:00")
        
        return {
            "triggered": True,
            "schedule_type": schedule_type,
            "time": time,
            "timestamp": self._get_timestamp()
        }
    
    @classmethod
    def get_metadata(cls) -> WorkflowNodeMetadata:
        return WorkflowNodeMetadata(
            name="ScheduledTriggerNode",
            description="Triggers workflow on a schedule",
            category="trigger",
            inputs=[
                WorkflowNodeInput("schedule_type", "string", "Schedule type (daily, weekly, monthly)", False, "daily"),
                WorkflowNodeInput("time", "string", "Time to trigger (HH:MM)", False, "09:00")
            ],
            outputs=[
                WorkflowNodeOutput("triggered", "boolean", "Whether trigger was activated"),
                WorkflowNodeOutput("schedule_type", "string", "Type of schedule"),
                WorkflowNodeOutput("time", "string", "Trigger time")
            ],
            icon="clock",
            color="#FF9800"
        )


class ManualTriggerNode(WorkflowTriggerNode):
    """
    Manual trigger node for testing and manual workflow execution.
    """
    
    def execute_workflow(self, config: Dict[str, Any], shared: SharedState) -> Dict[str, Any]:
        trigger_data = self.get_input_value("trigger_data", {})
        
        return {
            "triggered": True,
            "trigger_data": trigger_data,
            "timestamp": self._get_timestamp()
        }
    
    @classmethod
    def get_metadata(cls) -> WorkflowNodeMetadata:
        return WorkflowNodeMetadata(
            name="ManualTriggerNode",
            description="Manual trigger for testing workflows",
            category="trigger",
            inputs=[
                WorkflowNodeInput("trigger_data", "object", "Data to pass to workflow", False, {})
            ],
            outputs=[
                WorkflowNodeOutput("triggered", "boolean", "Whether trigger was activated"),
                WorkflowNodeOutput("trigger_data", "object", "Trigger data")
            ],
            icon="play",
            color="#2196F3"
        ) 