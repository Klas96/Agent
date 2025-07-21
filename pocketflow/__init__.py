"""
PocketFlow - A minimalist LLM framework
"""

class ActionNode:
    """Helper class for action transitions"""
    def __init__(self, node, action):
        self.node = node
        self.action = action
    
    def __rshift__(self, other):
        if not hasattr(self.node, '_transitions'):
            self.node._transitions = {}
        self.node._transitions[self.action] = other
        return None

class Node:
    """Base class for all nodes"""
    def __init__(self, max_retries=1, wait=0):
        self.max_retries = max_retries
        self.wait = wait
        self.cur_retry = 0
        self.params = {}
    
    def set_params(self, params):
        self.params = params
    
    def prep(self, shared):
        """Prepare data from shared store"""
        return None
    
    def exec(self, prep_res):
        """Execute the node's logic"""
        raise NotImplementedError
    
    def post(self, shared, prep_res, exec_res):
        """Post-process and write back to shared store"""
        return "default"
    
    def run(self, shared):
        """Run the complete node cycle"""
        prep_res = self.prep(shared)
        exec_res = self.exec(prep_res)
        return self.post(shared, prep_res, exec_res)
    
    def __sub__(self, action):
        """Create an ActionNode for action transitions"""
        return ActionNode(self, action)
    
    def __rshift__(self, other):
        """Default transition"""
        if not hasattr(self, '_transitions'):
            self._transitions = {}
        self._transitions['default'] = other
        return None

class Flow:
    """A flow orchestrates a graph of nodes"""
    def __init__(self, start=None):
        self.start = start
        self.transitions = {}
    
    def run(self, shared):
        """Run the flow starting from the start node"""
        if not self.start:
            return
        
        current = self.start
        while current:
            action = current.run(shared)
            if hasattr(current, '_transitions') and action in current._transitions:
                current = current._transitions[action]
            else:
                break

# Export the classes
__all__ = ['Node', 'Flow', 'ActionNode']
