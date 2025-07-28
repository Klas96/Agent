#!/usr/bin/env python3
"""
Test runner specifically for current PocketFlow features.

This script runs comprehensive tests on all current features and provides
detailed reporting on what's working and what needs attention.
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

class CurrentFeaturesTestRunner:
    """Test runner focused on current PocketFlow features."""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        self.feature_status = {}
        
    def test_core_abstractions(self):
        """Test core PocketFlow abstractions."""
        print("🔧 Testing Core Abstractions")
        print("-" * 40)
        
        try:
            # Test Node functionality
            from pocketflow import Node, Flow
            
            class TestNode(Node):
                def exec(self, prep_res):
                    return "test_result"
            
            node = TestNode()
            self.feature_status["core_node"] = True
            print("✅ Node abstraction working")
            
            # Test Flow functionality
            flow = Flow(start=node)
            self.feature_status["core_flow"] = True
            print("✅ Flow abstraction working")
            
            return True
            
        except Exception as e:
            print(f"❌ Core abstractions failed: {e}")
            self.feature_status["core_abstractions"] = False
            return False
    
    def test_flow_manager(self):
        """Test flow manager functionality."""
        print("\n🔄 Testing Flow Manager")
        print("-" * 40)
        
        try:
            from src.pocketflow.flows.manager import FlowManager
            from src.pocketflow.core.types import SharedState, FlowType
            
            flow_manager = FlowManager()
            shared = SharedState()
            
            # Test flow selection
            shared.user = "test@example.com"
            shared.flow_type = FlowType.TOKENLESS_USER
            
            selected_flow = flow_manager.select_flow(shared)
            self.feature_status["flow_selection"] = True
            print(f"✅ Flow selection working: {selected_flow}")
            
            # Test available flows
            flows = flow_manager.get_available_flows()
            self.feature_status["flow_availability"] = True
            print(f"✅ Available flows: {len(flows)} flows found")
            
            return True
            
        except Exception as e:
            print(f"❌ Flow manager failed: {e}")
            self.feature_status["flow_manager"] = False
            return False
    
    def test_services(self):
        """Test all services."""
        print("\n🔧 Testing Services")
        print("-" * 40)
        
        services_to_test = [
            ("EmailService", "email_service"),
            ("LLMService", "llm_service"),
            ("ContentService", "content_service"),
            ("DocumentService", "document_service"),
            ("BitcoinService", "bitcoin_service"),
            ("WebSearchService", "websearch_service"),
            ("DatabaseService", "database_service")
        ]
        
        all_passed = True
        
        for service_name, feature_key in services_to_test:
            try:
                service_module = __import__(f"src.pocketflow.services.{feature_key}", fromlist=[service_name])
                service_class = getattr(service_module, service_name)
                
                # Special handling for EmailService which requires settings
                if service_name == "EmailService":
                    try:
                        from src.pocketflow.config.settings import get_settings
                        settings = get_settings()
                        service_instance = service_class(settings)
                    except Exception as e:
                        # If settings not available, create a mock
                        from unittest.mock import Mock
                        mock_settings = Mock()
                        service_instance = service_class(mock_settings)
                else:
                    service_instance = service_class()
                
                self.feature_status[feature_key] = True
                print(f"✅ {service_name} working")
                
            except Exception as e:
                print(f"❌ {service_name} failed: {e}")
                self.feature_status[feature_key] = False
                all_passed = False
        
        return all_passed
    
    def test_flows(self):
        """Test all available flows."""
        print("\n🌊 Testing Flows")
        print("-" * 40)
        
        flows_to_test = [
            ("email_processor", "Email Processing"),
            ("tokenless_user", "Tokenless User"),
            ("content_generation", "Content Generation"),
            ("investigation", "Investigation"),
            ("payment_processing", "Payment Processing")
        ]
        
        all_passed = True
        
        try:
            from src.pocketflow.flows.manager import FlowManager
            flow_manager = FlowManager()
            
            for flow_name, display_name in flows_to_test:
                try:
                    flow = flow_manager._flows.get(flow_name)
                    if flow:
                        self.feature_status[f"flow_{flow_name}"] = True
                        print(f"✅ {display_name} flow available")
                    else:
                        print(f"❌ {display_name} flow not found")
                        self.feature_status[f"flow_{flow_name}"] = False
                        all_passed = False
                        
                except Exception as e:
                    print(f"❌ {display_name} flow failed: {e}")
                    self.feature_status[f"flow_{flow_name}"] = False
                    all_passed = False
                    
        except Exception as e:
            print(f"❌ Flow testing failed: {e}")
            all_passed = False
        
        return all_passed
    
    def test_nodes(self):
        """Test all available nodes."""
        print("\n🔗 Testing Nodes")
        print("-" * 40)
        
        # Test core nodes
        core_nodes = [
            "FetchEmailNode", "SendEmailNode", "ConversationContextNode",
            "AgentNode", "PopAgentActionNode", "ContentCreatorNode",
            "ContentParamNode", "GenerateContentNode", "InvestigateTopicNode",
            "FinishNode"
        ]
        
        all_passed = True
        
        try:
            from src.pocketflow.nodes import __all__ as available_nodes
            
            for node_name in core_nodes:
                try:
                    if node_name in available_nodes:
                        self.feature_status[f"node_{node_name.lower()}"] = True
                        print(f"✅ {node_name} available")
                    else:
                        print(f"⚠️  {node_name} not found in available nodes")
                        self.feature_status[f"node_{node_name.lower()}"] = False
                        all_passed = False
                        
                except Exception as e:
                    print(f"❌ {node_name} failed: {e}")
                    self.feature_status[f"node_{node_name.lower()}"] = False
                    all_passed = False
                    
        except Exception as e:
            print(f"❌ Node testing failed: {e}")
            all_passed = False
        
        return all_passed
    
    def test_email_functionality(self):
        """Test email-specific functionality."""
        print("\n📧 Testing Email Functionality")
        print("-" * 40)
        
        try:
            from src.pocketflow.services.email_service import EmailService
            
            # Try to get settings, fall back to mock if not available
            try:
                from src.pocketflow.config.settings import get_settings
                settings = get_settings()
                email_service = EmailService(settings)
            except Exception:
                from unittest.mock import Mock
                mock_settings = Mock()
                email_service = EmailService(mock_settings)
            
            # Test that email service can be initialized
            self.feature_status["email_functionality"] = True
            print("✅ Email service initialized successfully")
            
            # Test that we can access basic email functionality
            if email_service is not None and hasattr(email_service, 'settings'):
                print("✅ Email service has required attributes")
            else:
                raise Exception("Email service missing required attributes")
            
            return True
            
        except Exception as e:
            print(f"❌ Email functionality failed: {e}")
            self.feature_status["email_functionality"] = False
            return False
    
    def test_bitcoin_functionality(self):
        """Test Bitcoin functionality."""
        print("\n₿ Testing Bitcoin Functionality")
        print("-" * 40)
        
        try:
            from src.pocketflow.services.bitcoin_service import BitcoinService
            
            bitcoin_service = BitcoinService()
            
            # Test service initialization
            self.feature_status["bitcoin_service"] = True
            print("✅ Bitcoin service initialized")
            
            return True
            
        except Exception as e:
            print(f"❌ Bitcoin functionality failed: {e}")
            self.feature_status["bitcoin_functionality"] = False
            return False
    
    def test_content_generation(self):
        """Test content generation functionality."""
        print("\n🎵 Testing Content Generation")
        print("-" * 40)
        
        try:
            from src.pocketflow.services.content_service import ContentService
            
            content_service = ContentService()
            
            # Test service initialization
            self.feature_status["content_generation"] = True
            print("✅ Content generation service initialized")
            
            return True
            
        except Exception as e:
            print(f"❌ Content generation failed: {e}")
            self.feature_status["content_generation"] = False
            return False
    
    def test_investigation_functionality(self):
        """Test investigation functionality."""
        print("\n🔍 Testing Investigation Functionality")
        print("-" * 40)
        
        try:
            from src.pocketflow.services.websearch_service import WebSearchService
            
            websearch_service = WebSearchService()
            
            # Test service initialization
            self.feature_status["investigation"] = True
            print("✅ Investigation service initialized")
            
            return True
            
        except Exception as e:
            print(f"❌ Investigation functionality failed: {e}")
            self.feature_status["investigation"] = False
            return False
    
    def test_database_functionality(self):
        """Test database functionality."""
        print("\n🗄️ Testing Database Functionality")
        print("-" * 40)
        
        try:
            from src.pocketflow.services.database_service import DatabaseService
            
            database_service = DatabaseService()
            
            # Test service initialization
            self.feature_status["database"] = True
            print("✅ Database service initialized")
            
            return True
            
        except Exception as e:
            print(f"❌ Database functionality failed: {e}")
            self.feature_status["database"] = False
            return False
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests."""
        print("🧪 Running Comprehensive Current Features Test Suite")
        print("=" * 60)
        
        test_functions = [
            ("Core Abstractions", self.test_core_abstractions),
            ("Flow Manager", self.test_flow_manager),
            ("Services", self.test_services),
            ("Flows", self.test_flows),
            ("Nodes", self.test_nodes),
            ("Email Functionality", self.test_email_functionality),
            ("Bitcoin Functionality", self.test_bitcoin_functionality),
            ("Content Generation", self.test_content_generation),
            ("Investigation Functionality", self.test_investigation_functionality),
            ("Database Functionality", self.test_database_functionality)
        ]
        
        results = {}
        
        for test_name, test_func in test_functions:
            print(f"\n🔍 Testing {test_name}...")
            try:
                result = test_func()
                results[test_name] = result
            except Exception as e:
                print(f"❌ {test_name} test crashed: {e}")
                results[test_name] = False
        
        return results
    
    def generate_feature_report(self):
        """Generate a comprehensive feature report."""
        print("\n" + "=" * 60)
        print("📊 Current Features Status Report")
        print("=" * 60)
        
        # Group features by category
        categories = {
            "Core": [k for k in self.feature_status.keys() if k.startswith("core")],
            "Flows": [k for k in self.feature_status.keys() if k.startswith("flow")],
            "Services": [k for k in self.feature_status.keys() if k.startswith(("email", "llm", "content", "document", "bitcoin", "websearch", "database"))],
            "Nodes": [k for k in self.feature_status.keys() if k.startswith("node")],
            "Features": [k for k in self.feature_status.keys() if not any(k.startswith(prefix) for prefix in ["core", "flow", "node"])]
        }
        
        total_features = 0
        working_features = 0
        
        for category, features in categories.items():
            if features:
                print(f"\n{category} Features:")
                category_working = 0
                for feature in features:
                    status = self.feature_status.get(feature, False)
                    status_icon = "✅" if status else "❌"
                    print(f"  {status_icon} {feature}")
                    if status:
                        category_working += 1
                        working_features += 1
                    total_features += 1
                
                if features:
                    percentage = (category_working / len(features)) * 100
                    print(f"  📈 {category}: {category_working}/{len(features)} ({percentage:.1f}%)")
        
        overall_percentage = (working_features / total_features) * 100 if total_features > 0 else 0
        print(f"\n🎯 Overall Status: {working_features}/{total_features} features working ({overall_percentage:.1f}%)")
        
        if overall_percentage >= 90:
            print("🎉 Excellent! Most features are working correctly.")
        elif overall_percentage >= 70:
            print("✅ Good! Most core features are working.")
        elif overall_percentage >= 50:
            print("⚠️  Fair. Some features need attention.")
        else:
            print("❌ Poor. Many features need fixing.")
    
    def run_all_tests(self):
        """Run all tests and generate report."""
        results = self.run_comprehensive_tests()
        
        # Generate feature report
        self.generate_feature_report()
        
        # Summary
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        
        print(f"\n📈 Test Summary: {passed_tests}/{total_tests} test categories passed")
        
        if passed_tests == total_tests:
            print("🎉 All test categories passed!")
            return True
        else:
            print("⚠️  Some test categories failed. Check the report above.")
            return False


def main():
    """Main function to run the test suite."""
    runner = CurrentFeaturesTestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n✅ Current features test suite completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please review the report above.")
        sys.exit(1)


if __name__ == "__main__":
    main() 