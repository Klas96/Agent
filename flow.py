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

fetch >> context >> agent
# After agent, always go to pop_action or finish
agent - "generate" >> pop_action
agent - "investigate" >> pop_action
agent - "send" >> pop_action
agent - "finish" >> pop_action  # Route finish to pop_action for uniformity
agent >> pop_action
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