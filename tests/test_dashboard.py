#!/usr/bin/env python3
"""
Test script for the dashboard application.
"""

import os
import sys
from pathlib import Path

# Add paths to Python path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent

# Add paths to Python path
sys.path.insert(0, str(parent_dir / "src"))
sys.path.insert(0, str(parent_dir.parent / "dashboard" / "src"))

# Set environment variables for testing
os.environ.setdefault('EMAIL_HOST', 'localhost')
os.environ.setdefault('EMAIL_USERNAME', 'test@example.com')
os.environ.setdefault('EMAIL_PASSWORD', 'testpassword')
os.environ.setdefault('DATABASE_URL', 'postgresql://pocketflow:pocketflow_password@localhost:5432/pocketflow')

def test_dashboard_import():
    """Test that the dashboard can be imported successfully."""
    try:
        print("Testing dashboard import...")
        # Try different import paths
        try:
            from src.dashboard.web.app import create_app
        except ImportError:
            # Try alternative path
            sys.path.insert(0, str(parent_dir.parent / "dashboard" / "src"))
            from dashboard.web.app import create_app
        print("✓ Dashboard app imported successfully")
        return True
    except Exception as e:
        print(f"✗ Dashboard import failed: {e}")
        return False

def test_dashboard_app_creation():
    """Test that the dashboard app can be created successfully."""
    try:
        print("Testing dashboard app creation...")
        # Try different import paths
        try:
            from src.dashboard.web.app import create_app
        except ImportError:
            # Try alternative path
            sys.path.insert(0, str(parent_dir.parent / "dashboard" / "src"))
            from dashboard.web.app import create_app
        
        app = create_app()
        print("✓ Dashboard app created successfully")
        return True
    except Exception as e:
        print(f"✗ Dashboard app creation failed: {e}")
        return False

def test_dashboard_routes():
    """Test that dashboard routes are accessible."""
    try:
        print("Testing dashboard routes...")
        # Try different import paths
        try:
            from src.dashboard.web.app import create_app
        except ImportError:
            # Try alternative path
            sys.path.insert(0, str(parent_dir.parent / "dashboard" / "src"))
            from dashboard.web.app import create_app
        
        app = create_app()
        
        # Test that routes are registered
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        print(f"✓ Found {len(routes)} routes")
        
        # Check for key routes
        key_routes = ['/admin/', '/admin/users', '/admin/api/health']
        for route in key_routes:
            if route in routes:
                print(f"✓ Found route: {route}")
        
        return True
    except Exception as e:
        print(f"✗ Dashboard routes test failed: {e}")
        return False

def test_database_integration():
    """Test that the dashboard can connect to the database."""
    try:
        print("Testing database integration...")
        # Try different import paths
        try:
            from src.dashboard.web.app import create_app
        except ImportError:
            # Try alternative path
            sys.path.insert(0, str(parent_dir.parent / "dashboard" / "src"))
            from dashboard.web.app import create_app
        
        from pocketflow.services.database_service import DatabaseService
        
        # Test database service
        db = DatabaseService()
        users = db.get_all_users()
        print(f"✓ Database integration successful - {len(users)} users found")
        
        return True
    except Exception as e:
        print(f"✗ Database integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running dashboard tests...")
    print("=" * 50)
    
    success1 = test_dashboard_import()
    print()
    
    success2 = test_dashboard_app_creation()
    print()
    
    success3 = test_dashboard_routes()
    print()
    
    success4 = test_database_integration()
    print()
    
    if success1 and success2 and success3 and success4:
        print("🎉 All dashboard tests passed!")
        exit(0)
    else:
        print("❌ Some dashboard tests failed!")
        exit(1) 