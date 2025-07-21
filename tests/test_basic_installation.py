#!/usr/bin/env python3
"""
Basic installation test for PocketFlow
"""

import sys
import os
import pytest

# Add the application directory to the path
sys.path.insert(0, '/opt/pocketflow')

def test_imports():
    """Test that all main components can be imported"""
    try:
        from pocketflow import Flow, Node
        print("✓ PocketFlow core imports successful")
    except ImportError as e:
        pytest.fail(f"Failed to import PocketFlow core: {e}")
    
    try:
        from flow import flow
        print("✓ Flow import successful")
    except ImportError as e:
        pytest.fail(f"Failed to import flow: {e}")
    
    try:
        from nodes import (
            FetchEmailNode, ConversationContextNode, AgentNode,
            ContentCreatorNode, ContentParamNode, InvestigateTopicNode, 
            SendEmailNode, PostProcessNode, PopAgentActionNode
        )
        print("✓ All node imports successful")
    except ImportError as e:
        pytest.fail(f"Failed to import nodes: {e}")

def test_flow_creation():
    """Test that the flow can be created"""
    from flow import flow
    assert flow is not None
    print("✓ Flow creation successful")

def test_virtual_environment():
    """Test that we're running in the correct virtual environment"""
    venv_path = "/opt/pocketflow/venv"
    assert os.path.exists(venv_path), "Virtual environment should exist"
    assert os.path.exists(os.path.join(venv_path, "bin", "python")), "Python should exist in venv"
    print("✓ Virtual environment setup correct")

def test_dependencies():
    """Test that key dependencies are available"""
    try:
        import torch
        print(f"✓ PyTorch version: {torch.__version__}")
    except ImportError as e:
        pytest.fail(f"PyTorch not available: {e}")
    
    try:
        import openai
        print("✓ OpenAI library available")
    except ImportError as e:
        pytest.fail(f"OpenAI library not available: {e}")
    
    try:
        import requests
        print("✓ Requests library available")
    except ImportError as e:
        pytest.fail(f"Requests library not available: {e}")

def test_service_user():
    """Test that the service user exists"""
    import pwd
    try:
        pwd.getpwnam('pocketflow')
        print("✓ Service user 'pocketflow' exists")
    except KeyError:
        pytest.fail("Service user 'pocketflow' does not exist")

def test_directories():
    """Test that required directories exist and are accessible"""
    required_dirs = [
        "/opt/pocketflow",
        "/opt/pocketflow/data",
        "/var/log/pocketflow",
        "/etc/pocketflow"
    ]
    
    for directory in required_dirs:
        assert os.path.exists(directory), f"Directory {directory} should exist"
        assert os.access(directory, os.R_OK), f"Directory {directory} should be readable"
        print(f"✓ Directory {directory} exists and accessible")

def test_service_file():
    """Test that the systemd service file exists"""
    service_file = "/etc/systemd/system/pocketflow.service"
    assert os.path.exists(service_file), "Systemd service file should exist"
    print("✓ Systemd service file exists")

if __name__ == "__main__":
    # Run the tests
    print("Running PocketFlow installation tests...")
    print("=" * 50)
    
    test_functions = [
        test_imports,
        test_flow_creation,
        test_virtual_environment,
        test_dependencies,
        test_service_user,
        test_directories,
        test_service_file
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"Tests completed: {passed} passed, {failed} failed")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("🎉 All tests passed! Installation is working correctly.")
