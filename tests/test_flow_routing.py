#!/usr/bin/env python3
"""
Test script to verify flow routing is working correctly.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.pocketflow.core.flow import Flow, FlowBuilder
from src.pocketflow.core.node import Node
from src.pocketflow.core.types import SharedState, NodeResult, FlowType
from src.pocketflow.utils.logging import get_logger

logger = get_logger("TestFlowRouting")

class TestNode(Node):
    """Test node that returns a specific route."""
    
    def __init__(self, name: str, return_route: str):
        super().__init__(name)
        self.return_route = return_route
    
    def prep(self, shared: SharedState):
        return "test_data"
    
    def exec(self, prep_result):
        return "exec_result"
    
    def post(self, shared: SharedState, prep_result, exec_result):
        logger.info(f"TestNode {self.name} returning route: {self.return_route}")
        return self.return_route

def test_flow_routing():
    """Test that flow routing works correctly."""
    
    # Create a simple flow with routing
    flow = (FlowBuilder("test_flow", FlowType.TOKENED_USER)
            .add_step("step1", TestNode("step1", "finish"))
            .add_step("step2", TestNode("step2", "default"))
            .add_step("finish", TestNode("finish", "default"))
            .set_start("step1")
            .add_end_step("finish")
            .add_routing("step1", "finish", "finish")
            .add_routing("step1", "default", "step2")
            .add_routing("step2", "default", "finish")
            .build())
    
    # Create shared state
    shared = SharedState()
    
    # Run the flow
    logger.info("Testing flow routing...")
    result = flow.run(shared)
    
    logger.info(f"Flow result: {result}")
    logger.info(f"Flow success: {result.success}")
    logger.info(f"Flow error: {result.error}")
    logger.info(f"Flow metadata: {result.metadata}")
    
    return result.success

if __name__ == "__main__":
    success = test_flow_routing()
    if success:
        print("✅ Flow routing test passed!")
    else:
        print("❌ Flow routing test failed!")
        sys.exit(1) 