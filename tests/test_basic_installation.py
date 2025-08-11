#!/usr/bin/env python3
"""
Basic installation test for PocketFlow (Updated for New Architecture)
"""

import sys
import os
import pytest

# Add the application directory to the path
sys.path.insert(0, '/opt/pocketflow')

def test_new_architecture_imports():
    """Test that all new modular architecture components can be imported"""
    try:
        from src.pocketflow import flow_manager, get_settings
        print("✓ New modular architecture imports successful")
    except ImportError as e:
        pytest.fail(f"Failed to import new modular architecture: {e}")
    
    try:
        from src.pocketflow.core.types import SharedState, EmailData, AgentAction
        print("✓ Core types imports successful")
    except ImportError as e:
        pytest.fail(f"Failed to import core types: {e}")
    
    try:
        from src.pocketflow.services import (
            email_service, llm_service, content_service, 
            bitcoin_service, websearch_service, database_service
        )
        print("✓ Service layer imports successful")
    except ImportError as e:
        pytest.fail(f"Failed to import service layer: {e}")

def test_flow_manager():
    """Test that the flow manager can be created and used"""
    try:
        from src.pocketflow import flow_manager
        assert flow_manager is not None
        print("✓ Flow manager creation successful")
    except Exception as e:
        pytest.fail(f"Failed to create flow manager: {e}")

def test_settings():
    """Test that settings can be loaded"""
    try:
        from src.pocketflow import get_settings
        settings = get_settings()
        assert settings is not None
        assert hasattr(settings, 'ENVIRONMENT')
        print("✓ Settings loading successful")
    except Exception as e:
        pytest.fail(f"Failed to load settings: {e}")

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
    
    try:
        import pydantic_settings
        print("✓ Pydantic-settings available")
    except ImportError as e:
        pytest.fail(f"Pydantic-settings not available: {e}")

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
        "/opt/pocketflow/src",
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

def test_database_service():
    """Test that database service can be initialized"""
    try:
        from src.pocketflow.services import database_service
        assert database_service is not None
        print("✓ Database service initialization successful")
    except Exception as e:
        pytest.fail(f"Failed to initialize database service: {e}")

def test_new_architecture_structure():
    """Test that new architecture directories exist"""
    required_modules = [
        "src/pocketflow/core",
        "src/pocketflow/services", 
        "src/pocketflow/nodes",
        "src/pocketflow/flows",
        "src/pocketflow/config",
        "src/pocketflow/utils"
    ]
    
    for module in required_modules:
        module_path = os.path.join("/opt/pocketflow", module)
        assert os.path.exists(module_path), f"Module {module} should exist"
        print(f"✓ Module {module} exists")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
