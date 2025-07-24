#!/usr/bin/env python3
"""
Simple installation test for PocketFlow
Tests basic installation without importing the full architecture
"""

import sys
import os
import pytest

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

def test_python_files_exist():
    """Test that key Python files exist"""
    key_files = [
        "/opt/pocketflow/main.py",
        "/opt/pocketflow/src/pocketflow/__init__.py",
        "/opt/pocketflow/src/pocketflow/config/settings.py",
        "/opt/pocketflow/src/pocketflow/core/node.py",
        "/opt/pocketflow/src/pocketflow/core/flow.py",
        "/opt/pocketflow/src/pocketflow/services/__init__.py",
        "/opt/pocketflow/src/pocketflow/nodes/__init__.py",
        "/opt/pocketflow/src/pocketflow/flows/__init__.py"
    ]
    
    for file_path in key_files:
        assert os.path.exists(file_path), f"File {file_path} should exist"
        print(f"✓ File {file_path} exists")

def test_settings_file_content():
    """Test that settings file has correct imports"""
    settings_file = "/opt/pocketflow/src/pocketflow/config/settings.py"
    assert os.path.exists(settings_file), "Settings file should exist"
    
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Check for correct imports
    assert "from pydantic_settings import BaseSettings" in content, "Should import BaseSettings from pydantic_settings"
    assert "from pydantic import Field" in content, "Should import Field from pydantic"
    print("✓ Settings file has correct imports")

def test_requirements():
    """Test that requirements are installed"""
    try:
        import numpy
        print("✓ NumPy available")
    except ImportError:
        print("⚠ NumPy not available")
    
    try:
        import yaml
        print("✓ PyYAML available")
    except ImportError:
        print("⚠ PyYAML not available")
    
    try:
        import dotenv
        print("✓ python-dotenv available")
    except ImportError:
        print("⚠ python-dotenv not available")

def test_environment_variables():
    """Test that environment variables can be loaded"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ Environment variables can be loaded")
    except Exception as e:
        print(f"⚠ Environment loading issue: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 