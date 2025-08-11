#!/usr/bin/env python3
"""
Debug script to test AgentNode initialization and identify logger issues.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_agent_node_creation():
    """Test AgentNode creation and logger initialization."""
    print("🔧 Testing AgentNode creation...")
    
    try:
        from src.pocketflow.nodes.agent.core import AgentNode
        
        print("✅ Import successful")
        
        # Test creating the node
        print("🔧 Creating AgentNode...")
        node = AgentNode("test_agent")
        print("✅ AgentNode created successfully")
        
        # Check if logger is properly set
        print(f"🔧 Checking logger attribute...")
        print(f"   Has logger attribute: {hasattr(node, 'logger')}")
        if hasattr(node, 'logger'):
            print(f"   Logger type: {type(node.logger)}")
            print(f"   Logger name: {node.logger.name}")
        else:
            print("❌ Logger attribute is missing!")
            return False
        
        # Test logger functionality
        print("🔧 Testing logger functionality...")
        node.logger.info("Test log message")
        print("✅ Logger functionality test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during AgentNode creation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_node_process():
    """Test AgentNode process method."""
    print("\n🔧 Testing AgentNode process method...")
    
    try:
        from src.pocketflow.nodes.agent.core import AgentNode
        from src.pocketflow.core.types import SharedState
        
        # Create node
        node = AgentNode("test_agent")
        
        # Create shared state
        shared = SharedState()
        shared.user = "test@example.com"
        shared.email = {"from": "test@example.com", "body": "Hello"}
        
        # Test process method
        print("🔧 Calling process method...")
        result = node.process(shared)
        print(f"✅ Process method completed: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during process method: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎯 AgentNode Debug Test")
    print("=" * 50)
    
    # Test creation
    creation_success = test_agent_node_creation()
    
    # Test process method
    process_success = test_agent_node_process()
    
    print("\n📊 Results:")
    print(f"   Creation test: {'✅ PASS' if creation_success else '❌ FAIL'}")
    print(f"   Process test: {'✅ PASS' if process_success else '❌ FAIL'}")

if __name__ == "__main__":
    main() 