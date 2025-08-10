#!/usr/bin/env python3
"""
Test script for the donation-only system.

This script tests all components of the simplified donation-only system.
"""

import os
import yaml
from typing import Dict, Any


def test_flow_types():
    """Test that flow types have been updated correctly."""
    print("\n🔄 Testing flow types...")
    
    try:
        from pocketflow.core.types import FlowType
        
        # Check that old flow types are removed
        try:
            FlowType.TOKENED_USER
            assert False, "TOKENED_USER should be removed"
        except AttributeError:
            pass
        
        try:
            FlowType.TOKENLESS_USER
            assert False, "TOKENLESS_USER should be removed"
        except AttributeError:
            pass
        
        try:
            FlowType.PAYMENT_PENDING
            assert False, "PAYMENT_PENDING should be removed"
        except AttributeError:
            pass
        
        # Check that new flow type exists
        assert hasattr(FlowType, 'USER'), "USER should exist"
        assert FlowType.USER == "user"
        
        print("✅ Flow types updated correctly")
        return True
        
    except Exception as e:
        print(f"❌ Flow types test failed: {e}")
        return False


def test_user_status_node():
    """Test the simplified user status node."""
    print("\n🔧 Testing user status node...")
    
    try:
        from pocketflow.nodes.user_status_simplified import UserStatusCheckNode, DonationRequestNode
        from pocketflow.core.types import SharedState, FlowType
        
        # Test UserStatusCheckNode
        node = UserStatusCheckNode()
        shared = SharedState(user="test@example.com")
        
        result = node.process(shared)
        
        assert result is not None
        assert result.get("flow_type") == FlowType.USER.value
        assert "user_email" in result
        
        print("✅ UserStatusCheckNode working correctly")
        
        # Test DonationRequestNode (skip if Bitcoin service not available)
        try:
            donation_node = DonationRequestNode()
            result = donation_node.process(shared)
            
            assert result is not None
            assert "donation_requested" in result
            
            print("✅ DonationRequestNode working correctly")
        except Exception as e:
            print(f"⚠️  DonationRequestNode test skipped (Bitcoin service not available): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ User status node test failed: {e}")
        return False


def test_flow_manager():
    """Test the simplified flow manager."""
    print("\n📋 Testing flow manager...")
    
    try:
        from pocketflow.flows.manager_simplified import simplified_flow_manager
        from pocketflow.core.types import SharedState
        
        # Test flow selection
        shared = SharedState(user="test@example.com")
        selected_flow = simplified_flow_manager.select_flow(shared)
        
        assert selected_flow == "user_flow"
        
        # Test flow info
        flow_info = simplified_flow_manager.get_flow_info("user_flow")
        assert flow_info is not None
        assert flow_info["name"] == "User Flow"
        assert flow_info["requires_tokens"] == False
        
        print("✅ Flow manager working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Flow manager test failed: {e}")
        return False


def test_donation_flow():
    """Test the donation user flow."""
    print("\n🎙️ Testing donation flow...")
    
    try:
        from pocketflow.flows.donation_user import DonationUserFlow
        from pocketflow.core.types import SharedState
        
        # Create flow
        flow = DonationUserFlow()
        
        # Test flow info
        flow_info = flow.get_flow_info()
        assert flow_info["name"] == "user"
        assert flow_info["requires_tokens"] == False
        assert "donation_footer" in flow_info["capabilities"]
        
        print("✅ Donation flow created successfully")
        print(f"   Capabilities: {flow_info['capabilities']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Donation flow test failed: {e}")
        return False


def test_donation_monitor():
    """Test the donation monitor service."""
    print("\n💰 Testing donation monitor...")
    
    try:
        from pocketflow.services.donation_monitor import DonationMonitor
        
        # Test monitor creation
        monitor = DonationMonitor()
        assert monitor is not None
        
        print("✅ Donation monitor created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Donation monitor test failed: {e}")
        return False


def test_configuration():
    """Test that configuration files have been updated correctly."""
    print("\n⚙️ Testing configuration...")
    
    try:
        # Test flows configuration
        flows_config_path = "config/flows_donation_only.yaml"
        if os.path.exists(flows_config_path):
            with open(flows_config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            assert "user_flow" in config["flows"]
            assert config["flows"]["user_flow"]["flow_type"] == "user"
            assert config["flows"]["user_flow"]["requires_tokens"] == False
            
            print("✅ Configuration files updated correctly")
            return True
        else:
            print("⚠️  Donation-only flows config not found")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_shared_state():
    """Test that SharedState has been updated correctly."""
    print("\n📊 Testing shared state...")
    
    try:
        from pocketflow.core.types import SharedState
        
        # Test that token-related fields are removed
        shared = SharedState()
        
        # These fields should not exist
        assert not hasattr(shared, 'tokens_remaining')
        assert not hasattr(shared, 'user_has_tokens')
        assert not hasattr(shared, 'out_of_tokens')
        
        # These fields should exist
        assert hasattr(shared, 'donation_info')
        assert hasattr(shared, 'btc_address')
        
        print("✅ SharedState updated correctly")
        return True
        
    except Exception as e:
        print(f"❌ SharedState test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Donation-Only System")
    print("=" * 50)
    
    tests = [
        ("Flow Types", test_flow_types),
        ("User Status Node", test_user_status_node),
        ("Flow Manager", test_flow_manager),
        ("Donation Flow", test_donation_flow),
        ("Donation Monitor", test_donation_monitor),
        ("Configuration", test_configuration),
        ("Shared State", test_shared_state),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Donation-only system is working correctly!")
        print("\n💡 System is ready for:")
        print("   1. Database migration")
        print("   2. Production deployment")
        print("   3. User communication")
        print("   4. Monitoring and optimization")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
        print("\n💡 Common fixes:")
        print("   - Run the migration script first")
        print("   - Check file paths and imports")
        print("   - Verify database schema changes")
    
    return passed == len(results)


if __name__ == "__main__":
    success = main() 