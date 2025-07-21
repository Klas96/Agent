from pocketflow import Flow
from nodes import (
    FetchEmailNode, ConversationContextNode, AgentNode,
    ContentCreatorNode, ContentParamNode, InvestigateTopicNode, SendEmailNode, PostProcessNode,
    PopAgentActionNode
)

fetch = FetchEmailNode()
context = ConversationContextNode()
agent = AgentNode()
pop_action = PopAgentActionNode()
content_creator = ContentCreatorNode()
content_param = ContentParamNode()
investigate = InvestigateTopicNode()
send = SendEmailNode()
postprocess = PostProcessNode()

# Connect nodes
fetch >> context
context >> agent
# Handle no_email and no_context cases - just end the flow, main.py will restart it
# fetch - "no_email" >> fetch  # This creates infinite loop
# context - "no_context" >> fetch  # This would also create infinite loop
# After agent, always go to pop_action or finish
agent - "generate" >> pop_action
agent - "investigate" >> pop_action
agent - "send" >> pop_action
agent - "finish" >> postprocess  # Route finish directly to postprocess for simple responses
agent - "default" >> pop_action  # Handle default action
agent >> pop_action  # Fallback
# After pop_action, route to the correct node based on action type
pop_action - "generate" >> content_creator
pop_action - "send" >> send
pop_action - "investigate" >> investigate
pop_action - "finish" >> postprocess
# Route by subtype from content_creator to content_param
content_creator - "music" >> content_param
content_creator - "song" >> content_param
content_creator - "podcast" >> content_param
content_creator >> content_param  # fallback for any other subtype
content_param >> pop_action
investigate >> pop_action
send >> pop_action
postprocess >> fetch

flow = Flow(start=fetch) 