# src/pocketflow/nodes/workflow/agents.py
"""
Agent nodes for workflow system.
These nodes handle decision making, content creation, investigation, messaging, and postprocessing.
"""

from typing import Dict, Any
from ...core.node import Node
from ...core.types import SharedState
from ...services import llm_service, content_service, websearch_service, email_service
from ...config.settings import get_settings
from ...utils.logging import get_logger
from .base import WorkflowActionNode, WorkflowConditionNode, WorkflowTransformNode, WorkflowNodeMetadata, WorkflowNodeInput, WorkflowNodeOutput


class DecisionAgentNode(WorkflowConditionNode):
    """
    Decision agent node that analyzes content and makes decisions about workflow routing.
    This node uses LLM to analyze email content and determine the appropriate action.
    """
    
    def execute_workflow(self, config: Dict[str, Any], shared: SharedState) -> Dict[str, Any]:
        try:
            email_body = shared.get("email_body", "")
            email_subject = shared.get("email_subject", "")
            email_sender = shared.get("email_sender", "")
            
            # Create decision prompt
            decision_prompt = f"""
            Analyze this email and decide what action to take:
            
            Subject: {email_subject}
            From: {email_sender}
            Body: {email_body}
            
            Possible actions:
            1. "content_creation" - If the email requests content generation (reports, summaries, etc.)
            2. "investigation" - If the email asks for research or investigation
            3. "simple_reply" - If the email needs a simple response
            4. "ignore" - If the email should be ignored
            
            Return your decision as a JSON object:
            {{
                "decision": "content_creation|investigation|simple_reply|ignore",
                "reason": "Brief explanation of the decision",
                "priority": "high|medium|low",
                "requires_content": true/false,
                "requires_research": true/false
            }}
            """
            
            # Use LLM service to make decision
            decision_response = llm_service.generate_text(decision_prompt)
            
            # Parse the decision (simplified for now)
            import json
            try:
                decision_data = json.loads(decision_response)
            except:
                decision_data = {
                    "decision": "simple_reply",
                    "reason": "Could not parse decision, defaulting to simple reply",
                    "priority": "medium",
                    "requires_content": False,
                    "requires_research": False
                }
            
            # Store decision in shared state
            shared["decision_result"] = decision_data
            shared["workflow_decision"] = decision_data["decision"]
            
            return {
                "decision": decision_data["decision"],
                "reason": decision_data["reason"],
                "priority": decision_data["priority"],
                "requires_content": decision_data.get("requires_content", False),
                "requires_research": decision_data.get("requires_research", False),
                "confidence": 0.8  # Placeholder confidence score
            }
            
        except Exception as e:
            self.logger.error(f"Error in decision agent: {e}")
            return {
                "decision": "simple_reply",
                "reason": f"Error occurred: {str(e)}",
                "priority": "low",
                "requires_content": False,
                "requires_research": False,
                "confidence": 0.0
            }
    
    @classmethod
    def get_metadata(cls) -> WorkflowNodeMetadata:
        return WorkflowNodeMetadata(
            name="DecisionAgentNode",
            description="AI agent that analyzes emails and makes routing decisions",
            category="agent",
            inputs=[
                WorkflowNodeInput("analysis_prompt", "string", "Custom analysis prompt", False, ""),
                WorkflowNodeInput("decision_threshold", "number", "Confidence threshold for decisions", False, 0.7)
            ],
            outputs=[
                WorkflowNodeOutput("decision", "string", "Decision made (content_creation|investigation|simple_reply|ignore)"),
                WorkflowNodeOutput("reason", "string", "Reason for the decision"),
                WorkflowNodeOutput("priority", "string", "Priority level (high|medium|low)"),
                WorkflowNodeOutput("requires_content", "boolean", "Whether content creation is needed"),
                WorkflowNodeOutput("requires_research", "boolean", "Whether research is needed"),
                WorkflowNodeOutput("confidence", "number", "Confidence score of the decision")
            ],
            icon="psychology",
            color="#9C27B0"
        )


class ContentCreatorNode(WorkflowActionNode):
    """
    Content creator node that generates various types of content based on email requests.
    This node can create reports, summaries, documents, and other content.
    """
    
    def execute_workflow(self, config: Dict[str, Any], shared: SharedState) -> Dict[str, Any]:
        try:
            email_body = shared.get("email_body", "")
            email_subject = shared.get("email_subject", "")
            content_type = self.get_input_value("content_type", "summary")
            template = self.get_input_value("template", "default")
            
            # Create content generation prompt
            content_prompt = f"""
            Create {content_type} based on this email request:
            
            Subject: {email_subject}
            Request: {email_body}
            
            Content type: {content_type}
            Template: {template}
            
            Generate professional, well-structured content that addresses the request.
            """
            
            # Generate content using the content service
            if content_type == "latex":
                content = content_service.generate_latex_document(content_prompt, template)
            elif content_type == "audio":
                content = content_service.generate_audio(content_prompt)
            elif content_type == "image":
                content = content_service.generate_image(content_prompt)
            else:
                content = content_service.generate_text(content_prompt)
            
            # Store content in shared state
            shared["generated_content"] = content
            shared["content_type"] = content_type
            
            return {
                "content": content,
                "content_type": content_type,
                "template": template,
                "word_count": len(content.split()) if isinstance(content, str) else 0,
                "generated_at": self._get_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Error in content creator: {e}")
            return {
                "content": f"Error generating content: {str(e)}",
                "content_type": content_type,
                "error": str(e)
            }
    
    @classmethod
    def get_metadata(cls) -> WorkflowNodeMetadata:
        return WorkflowNodeMetadata(
            name="ContentCreatorNode",
            description="Creates various types of content (text, LaTeX, audio, images)",
            category="agent",
            inputs=[
                WorkflowNodeInput("content_type", "string", "Type of content to create (text|latex|audio|image)", False, "text"),
                WorkflowNodeInput("template", "string", "Template to use for content generation", False, "default")
            ],
            outputs=[
                WorkflowNodeOutput("content", "string", "Generated content"),
                WorkflowNodeOutput("content_type", "string", "Type of content created"),
                WorkflowNodeOutput("template", "string", "Template used"),
                WorkflowNodeOutput("word_count", "number", "Number of words in content"),
                WorkflowNodeOutput("generated_at", "string", "When content was generated")
            ],
            icon="create",
            color="#4CAF50"
        )


class InvestigationNode(WorkflowActionNode):
    """
    Investigation node that performs research and gathers information.
    This node can search the web, analyze topics, and gather relevant data.
    """
    
    def execute_workflow(self, config: Dict[str, Any], shared: SharedState) -> Dict[str, Any]:
        try:
            email_body = shared.get("email_body", "")
            email_subject = shared.get("email_subject", "")
            search_query = self.get_input_value("search_query", email_subject)
            search_depth = self.get_input_value("search_depth", "medium")
            
            # Perform web search
            search_results = websearch_service.search_web(search_query, max_results=5)
            
            # Analyze and synthesize results
            analysis_prompt = f"""
            Analyze these search results and provide a comprehensive investigation:
            
            Query: {search_query}
            Email context: {email_body}
            
            Search results:
            {search_results}
            
            Provide:
            1. Key findings
            2. Relevant information
            3. Recommendations
            4. Sources
            """
            
            investigation_report = llm_service.generate_text(analysis_prompt)
            
            # Store investigation results in shared state
            shared["investigation_results"] = search_results
            shared["investigation_report"] = investigation_report
            shared["search_query"] = search_query
            
            return {
                "search_results": search_results,
                "investigation_report": investigation_report,
                "search_query": search_query,
                "search_depth": search_depth,
                "sources_count": len(search_results) if isinstance(search_results, list) else 1,
                "investigated_at": self._get_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Error in investigation: {e}")
            return {
                "search_results": [],
                "investigation_report": f"Error during investigation: {str(e)}",
                "search_query": search_query,
                "error": str(e)
            }
    
    @classmethod
    def get_metadata(cls) -> WorkflowNodeMetadata:
        return WorkflowNodeMetadata(
            name="InvestigationNode",
            description="Performs research and investigation on topics",
            category="agent",
            inputs=[
                WorkflowNodeInput("search_query", "string", "Search query for investigation", False, ""),
                WorkflowNodeInput("search_depth", "string", "Search depth (shallow|medium|deep)", False, "medium")
            ],
            outputs=[
                WorkflowNodeOutput("search_results", "array", "Raw search results"),
                WorkflowNodeOutput("investigation_report", "string", "Synthesized investigation report"),
                WorkflowNodeOutput("search_query", "string", "Query that was searched"),
                WorkflowNodeOutput("search_depth", "string", "Depth of search performed"),
                WorkflowNodeOutput("sources_count", "number", "Number of sources found"),
                WorkflowNodeOutput("investigated_at", "string", "When investigation was performed")
            ],
            icon="search",
            color="#FF9800"
        )


class MessageSendingNode(WorkflowActionNode):
    """
    Message sending node that sends emails and other communications.
    This node handles the actual sending of responses and messages.
    """
    
    def execute_workflow(self, config: Dict[str, Any], shared: SharedState) -> Dict[str, Any]:
        try:
            email_sender = shared.get("email_sender", "")
            email_subject = shared.get("email_subject", "")
            message_content = self.get_input_value("message_content", "")
            message_type = self.get_input_value("message_type", "email")
            
            # If no message content provided, try to get from shared state
            if not message_content:
                message_content = shared.get("generated_content", "")
                if not message_content:
                    message_content = shared.get("investigation_report", "")
            
            # Prepare email content
            if message_type == "email":
                # Use the original PocketFlow email service
                email_result = email_service.send_email(
                    to=email_sender,
                    subject=f"Re: {email_subject}",
                    body=message_content,
                    attachments=shared.get("attachments", [])
                )
                
                result = {
                    "sent": True,
                    "message_type": "email",
                    "recipient": email_sender,
                    "subject": f"Re: {email_subject}",
                    "content_length": len(message_content),
                    "sent_at": self._get_timestamp()
                }
            else:
                # For other message types (placeholder)
                result = {
                    "sent": True,
                    "message_type": message_type,
                    "recipient": email_sender,
                    "content_length": len(message_content),
                    "sent_at": self._get_timestamp()
                }
            
            # Store sending result in shared state
            shared["message_sent"] = result
            shared["response_content"] = message_content
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in message sending: {e}")
            return {
                "sent": False,
                "error": str(e),
                "message_type": message_type
            }
    
    @classmethod
    def get_metadata(cls) -> WorkflowNodeMetadata:
        return WorkflowNodeMetadata(
            name="MessageSendingNode",
            description="Sends emails and other messages",
            category="agent",
            inputs=[
                WorkflowNodeInput("message_content", "string", "Content of the message to send", False, ""),
                WorkflowNodeInput("message_type", "string", "Type of message (email|notification)", False, "email")
            ],
            outputs=[
                WorkflowNodeOutput("sent", "boolean", "Whether message was sent successfully"),
                WorkflowNodeOutput("message_type", "string", "Type of message sent"),
                WorkflowNodeOutput("recipient", "string", "Message recipient"),
                WorkflowNodeOutput("subject", "string", "Message subject"),
                WorkflowNodeOutput("content_length", "number", "Length of message content"),
                WorkflowNodeOutput("sent_at", "string", "When message was sent")
            ],
            icon="send",
            color="#2196F3"
        )


class PostProcessingNode(WorkflowTransformNode):
    """
    Post-processing node that handles final processing, logging, and cleanup.
    This node performs final transformations and prepares data for storage or further processing.
    """
    
    def execute_workflow(self, config: Dict[str, Any], shared: SharedState) -> Dict[str, Any]:
        try:
            # Gather all workflow data
            workflow_data = {
                "email_data": shared.get("email_data", {}),
                "decision_result": shared.get("decision_result", {}),
                "generated_content": shared.get("generated_content", ""),
                "investigation_results": shared.get("investigation_results", []),
                "message_sent": shared.get("message_sent", {}),
                "workflow_execution_time": self._get_timestamp()
            }
            
            # Perform post-processing tasks
            post_processing_tasks = self.get_input_value("post_processing_tasks", ["log", "summarize"])
            
            results = {}
            
            if "log" in post_processing_tasks:
                # Log the workflow execution
                self.logger.info(f"Workflow completed: {workflow_data}")
                results["logged"] = True
            
            if "summarize" in post_processing_tasks:
                # Create a summary of the workflow execution
                summary_prompt = f"""
                Create a brief summary of this workflow execution:
                
                Email: {workflow_data['email_data'].get('subject', 'No subject')}
                Decision: {workflow_data['decision_result'].get('decision', 'No decision')}
                Content Generated: {'Yes' if workflow_data['generated_content'] else 'No'}
                Investigation Performed: {'Yes' if workflow_data['investigation_results'] else 'No'}
                Message Sent: {'Yes' if workflow_data['message_sent'].get('sent', False) else 'No'}
                
                Provide a concise summary of what was accomplished.
                """
                
                summary = llm_service.generate_text(summary_prompt)
                results["summary"] = summary
                shared["workflow_summary"] = summary
            
            if "cleanup" in post_processing_tasks:
                # Clean up temporary data
                cleanup_keys = ["temp_data", "intermediate_results"]
                for key in cleanup_keys:
                    if key in shared:
                        del shared[key]
                results["cleaned_up"] = True
            
            # Store final results
            shared["workflow_completed"] = True
            shared["post_processing_results"] = results
            
            return {
                "workflow_data": workflow_data,
                "post_processing_results": results,
                "tasks_performed": post_processing_tasks,
                "completed_at": self._get_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Error in post-processing: {e}")
            return {
                "error": str(e),
                "workflow_data": {},
                "post_processing_results": {}
            }
    
    @classmethod
    def get_metadata(cls) -> WorkflowNodeMetadata:
        return WorkflowNodeMetadata(
            name="PostProcessingNode",
            description="Handles final processing, logging, and cleanup",
            category="agent",
            inputs=[
                WorkflowNodeInput("post_processing_tasks", "array", "Tasks to perform (log|summarize|cleanup)", False, ["log", "summarize"])
            ],
            outputs=[
                WorkflowNodeOutput("workflow_data", "object", "Complete workflow execution data"),
                WorkflowNodeOutput("post_processing_results", "object", "Results of post-processing tasks"),
                WorkflowNodeOutput("tasks_performed", "array", "Tasks that were performed"),
                WorkflowNodeOutput("completed_at", "string", "When post-processing completed")
            ],
            icon="settings",
            color="#607D8B"
        ) 