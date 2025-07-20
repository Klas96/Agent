"""
PocketFlow Integration Example

This example demonstrates the complete PocketFlow system with all features:
- Dynamic flow selection
- Service integrations
- Performance monitoring
- Error handling
- Configuration management
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pocketflow import (
    SharedState, FlowType, run_auto_select, run_flow,
    get_available_flows, get_flow_info,
    setup_logging, get_logger,
    performance_monitor
)
from pocketflow.utils.performance import monitor_performance


@monitor_performance("integration_example")
def run_integration_example():
    """Run the complete integration example."""
    logger = get_logger("IntegrationExample")
    
    logger.info("🚀 Starting PocketFlow Integration Example")
    
    # Test different user scenarios
    test_scenarios = [
        {
            "name": "Tokened User - Content Generation",
            "shared": SharedState(
                user="creator@example.com",
                flow_type=FlowType.TOKENED_USER,
                email={
                    "id": "email_1",
                    "from": "creator@example.com",
                    "to": "assistant@example.com",
                    "subject": "Generate a song",
                    "body": "Please generate a 2-minute song in the style of Daft Punk and send it to me.",
                    "thread_id": "thread_1"
                }
            )
        },
        {
            "name": "Tokened User - Investigation",
            "shared": SharedState(
                user="researcher@example.com",
                flow_type=FlowType.TOKENED_USER,
                email={
                    "id": "email_2",
                    "from": "researcher@example.com",
                    "to": "assistant@example.com",
                    "subject": "Research request",
                    "body": "Please research the latest developments in artificial intelligence and summarize your findings.",
                    "thread_id": "thread_2"
                }
            )
        },
        {
            "name": "Tokenless User",
            "shared": SharedState(
                user="newuser@example.com",
                flow_type=FlowType.TOKENLESS_USER,
                email={
                    "id": "email_3",
                    "from": "newuser@example.com",
                    "to": "assistant@example.com",
                    "subject": "I want to generate content",
                    "body": "Please generate a song for me.",
                    "thread_id": "thread_3"
                }
            )
        },
        {
            "name": "Payment Processing",
            "shared": SharedState(
                user="payer@example.com",
                flow_type=FlowType.PAYMENT_PENDING,
                email={
                    "id": "email_4",
                    "from": "payer@example.com",
                    "to": "assistant@example.com",
                    "subject": "Payment request",
                    "body": "I want to purchase tokens.",
                    "thread_id": "thread_4"
                }
            )
        },
        {
            "name": "General Email Processing",
            "shared": SharedState(
                user="user@example.com",
                flow_type=FlowType.TOKENED_USER,
                email={
                    "id": "email_5",
                    "from": "user@example.com",
                    "to": "assistant@example.com",
                    "subject": "Help me with a task",
                    "body": "Please help me organize my schedule for next week.",
                    "thread_id": "thread_5"
                }
            )
        }
    ]
    
    # Run each scenario
    results = []
    for i, scenario in enumerate(test_scenarios, 1):
        logger.info(f"\n=== Test Scenario {i}: {scenario['name']} ===")
        
        try:
            # Run with auto-selection
            result = run_auto_select(scenario["shared"])
            
            if result["success"]:
                logger.info(f"✅ {scenario['name']} completed successfully!")
                logger.info(f"   Final state keys: {list(result.get('final_state', {}).keys())}")
            else:
                logger.error(f"❌ {scenario['name']} failed: {result.get('error')}")
            
            results.append({
                "scenario": scenario["name"],
                "success": result["success"],
                "error": result.get("error"),
                "final_state_keys": list(result.get("final_state", {}).keys())
            })
            
        except Exception as e:
            logger.error(f"❌ Exception in {scenario['name']}: {e}")
            results.append({
                "scenario": scenario["name"],
                "success": False,
                "error": str(e),
                "final_state_keys": []
            })
    
    # Test manual flow selection
    logger.info("\n=== Testing Manual Flow Selection ===")
    
    manual_tests = [
        ("email_processor", "Manual Email Processor"),
        ("content_generation", "Manual Content Generation"),
        ("investigation", "Manual Investigation"),
        ("tokenless_user", "Manual Tokenless User"),
        ("payment_processing", "Manual Payment Processing")
    ]
    
    for flow_name, test_name in manual_tests:
        logger.info(f"Testing {test_name}...")
        
        # Create test shared state
        test_shared = SharedState(
            user="manual@example.com",
            flow_type=FlowType.TOKENED_USER,
            email={
                "id": f"manual_{flow_name}",
                "from": "manual@example.com",
                "to": "assistant@example.com",
                "subject": f"Manual test for {flow_name}",
                "body": "This is a manual test.",
                "thread_id": f"manual_thread_{flow_name}"
            }
        )
        
        try:
            result = run_flow(flow_name, test_shared)
            if result["success"]:
                logger.info(f"✅ {test_name} completed successfully!")
            else:
                logger.error(f"❌ {test_name} failed: {result.get('error')}")
        except Exception as e:
            logger.error(f"❌ Exception in {test_name}: {e}")
    
    # Test flow information
    logger.info("\n=== Testing Flow Information ===")
    
    # Get all available flows
    flows_info = get_available_flows()
    logger.info(f"Available flows: {[flow['name'] for flow in flows_info]}")
    
    # Get specific flow info
    for flow_name in ["email_processor", "content_generation", "investigation"]:
        info = get_flow_info(flow_name)
        if info:
            logger.info(f"Flow '{flow_name}' capabilities: {info.get('capabilities', [])}")
        else:
            logger.warning(f"Flow '{flow_name}' info not available")
    
    # Test performance monitoring
    logger.info("\n=== Testing Performance Monitoring ===")
    
    # Get performance metrics
    metrics = performance_monitor.get_metrics()
    if metrics["summary"]:
        summary = metrics["summary"]
        logger.info(f"Performance Summary:")
        logger.info(f"  Total operations: {summary.get('total_operations', 0)}")
        logger.info(f"  Success rate: {summary.get('success_rate', 0):.2%}")
        logger.info(f"  Average duration: {summary.get('average_duration', 0):.3f}s")
        logger.info(f"  Total duration: {summary.get('total_duration', 0):.3f}s")
    
    # Print results summary
    logger.info("\n=== Results Summary ===")
    
    successful_scenarios = [r for r in results if r["success"]]
    failed_scenarios = [r for r in results if not r["success"]]
    
    logger.info(f"Total scenarios tested: {len(results)}")
    logger.info(f"Successful scenarios: {len(successful_scenarios)}")
    logger.info(f"Failed scenarios: {len(failed_scenarios)}")
    logger.info(f"Success rate: {len(successful_scenarios) / len(results):.2%}")
    
    if successful_scenarios:
        logger.info("\nSuccessful scenarios:")
        for result in successful_scenarios:
            logger.info(f"  ✅ {result['scenario']}")
    
    if failed_scenarios:
        logger.info("\nFailed scenarios:")
        for result in failed_scenarios:
            logger.info(f"  ❌ {result['scenario']}: {result['error']}")
    
    logger.info("\n✅ PocketFlow Integration Example completed!")
    
    return {
        "total_scenarios": len(results),
        "successful_scenarios": len(successful_scenarios),
        "failed_scenarios": len(failed_scenarios),
        "success_rate": len(successful_scenarios) / len(results) if results else 0,
        "results": results
    }


def test_service_integration():
    """Test individual service integrations."""
    logger = get_logger("ServiceIntegrationTest")
    
    logger.info("\n=== Testing Service Integrations ===")
    
    # Test email service
    try:
        from pocketflow.services import email_service
        logger.info("✅ Email service imported successfully")
    except Exception as e:
        logger.error(f"❌ Email service import failed: {e}")
    
    # Test LLM service
    try:
        from pocketflow.services import llm_service
        logger.info("✅ LLM service imported successfully")
    except Exception as e:
        logger.error(f"❌ LLM service import failed: {e}")
    
    # Test content service
    try:
        from pocketflow.services import content_service
        logger.info("✅ Content service imported successfully")
    except Exception as e:
        logger.error(f"❌ Content service import failed: {e}")
    
    # Test Bitcoin service
    try:
        from pocketflow.services import bitcoin_service
        logger.info("✅ Bitcoin service imported successfully")
    except Exception as e:
        logger.error(f"❌ Bitcoin service import failed: {e}")
    
    # Test web search service
    try:
        from pocketflow.services import websearch_service
        logger.info("✅ Web search service imported successfully")
    except Exception as e:
        logger.error(f"❌ Web search service import failed: {e}")


def test_node_integration():
    """Test individual node integrations."""
    logger = get_logger("NodeIntegrationTest")
    
    logger.info("\n=== Testing Node Integrations ===")
    
    # Test email nodes
    try:
        from pocketflow.nodes import FetchEmailNode, SendEmailNode, ConversationContextNode
        logger.info("✅ Email nodes imported successfully")
    except Exception as e:
        logger.error(f"❌ Email nodes import failed: {e}")
    
    # Test agent nodes
    try:
        from pocketflow.nodes import AgentNode, PopAgentActionNode
        logger.info("✅ Agent nodes imported successfully")
    except Exception as e:
        logger.error(f"❌ Agent nodes import failed: {e}")
    
    # Test content nodes
    try:
        from pocketflow.nodes import ContentCreatorNode, ContentParamNode, GenerateContentNode
        logger.info("✅ Content nodes imported successfully")
    except Exception as e:
        logger.error(f"❌ Content nodes import failed: {e}")
    
    # Test investigation nodes
    try:
        from pocketflow.nodes import InvestigateTopicNode
        logger.info("✅ Investigation nodes imported successfully")
    except Exception as e:
        logger.error(f"❌ Investigation nodes import failed: {e}")
    
    # Test Bitcoin nodes
    try:
        from pocketflow.nodes import PurchaseTokensWithBitcoinNode
        logger.info("✅ Bitcoin nodes imported successfully")
    except Exception as e:
        logger.error(f"❌ Bitcoin nodes import failed: {e}")


def test_flow_integration():
    """Test individual flow integrations."""
    logger = get_logger("FlowIntegrationTest")
    
    logger.info("\n=== Testing Flow Integrations ===")
    
    # Test all flows
    flows_to_test = [
        ("EmailProcessorFlow", "Email Processor Flow"),
        ("TokenlessUserFlow", "Tokenless User Flow"),
        ("ContentGenerationFlow", "Content Generation Flow"),
        ("InvestigationFlow", "Investigation Flow"),
        ("PaymentProcessingFlow", "Payment Processing Flow")
    ]
    
    for flow_class_name, flow_display_name in flows_to_test:
        try:
            # Import the flow class
            exec(f"from pocketflow.flows import {flow_class_name}")
            logger.info(f"✅ {flow_display_name} imported successfully")
        except Exception as e:
            logger.error(f"❌ {flow_display_name} import failed: {e}")


def main():
    """Run the complete integration example."""
    # Set up logging
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("IntegrationExample")
    
    logger.info("🚀 Starting PocketFlow Integration Example")
    
    # Test service integrations
    test_service_integration()
    
    # Test node integrations
    test_node_integration()
    
    # Test flow integrations
    test_flow_integration()
    
    # Run the main integration example
    result = run_integration_example()
    
    # Print final summary
    logger.info("\n" + "="*50)
    logger.info("🎉 INTEGRATION EXAMPLE COMPLETED")
    logger.info("="*50)
    logger.info(f"Total scenarios: {result['total_scenarios']}")
    logger.info(f"Success rate: {result['success_rate']:.2%}")
    logger.info("="*50)
    
    return result


if __name__ == "__main__":
    main() 