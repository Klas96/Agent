"""
LLM-Enhanced Agentic PocketFlow Example

This example demonstrates the LLM-enhanced agentic approach where agents use
LLMs to make intelligent decisions instead of keyword matching.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pocketflow import SharedState, FlowType, setup_logging, get_logger
from pocketflow.agents.llm_enhanced_coordinator import LLMEnhancedCoordinatorAgent
from pocketflow.agents.llm_enhanced_research_agent import LLMEnhancedResearchAgent
from pocketflow.agents.content_agent import ContentAgent
from pocketflow.agents.email_agent import EmailAgent
from pocketflow.agents.payment_agent import PaymentAgent
from pocketflow.agents.base_agent import AgentAction


def setup_llm_agentic_system():
    """Set up the LLM-enhanced agentic system."""
    logger = get_logger("LLMAgenticExample")
    
    # Create LLM-enhanced coordinator agent
    coordinator = LLMEnhancedCoordinatorAgent()
    
    # Create specialized agents
    research_agent = LLMEnhancedResearchAgent()
    content_agent = ContentAgent()
    email_agent = EmailAgent()
    payment_agent = PaymentAgent()
    
    # Register agents with coordinator
    coordinator.register_agent(research_agent)
    coordinator.register_agent(content_agent)
    coordinator.register_agent(email_agent)
    coordinator.register_agent(payment_agent)
    
    logger.info("LLM-enhanced agentic system set up with all agents registered")
    
    return coordinator


def run_llm_agentic_workflow(coordinator, shared: SharedState):
    """Run the LLM-enhanced agentic workflow."""
    logger = get_logger("LLMAgenticWorkflow")
    
    logger.info("🚀 Starting LLM-enhanced agentic workflow")
    
    workflow_steps = []
    max_iterations = 10  # Prevent infinite loops
    
    for iteration in range(max_iterations):
        logger.info(f"\n=== Iteration {iteration + 1} ===")
        
        # Get current workflow status
        status = coordinator.get_workflow_status()
        logger.info(f"Current agent: {status['current_agent']}")
        logger.info(f"Task complete: {status['task_complete']}")
        
        # Check if workflow is complete
        if status['task_complete']:
            logger.info("✅ Workflow completed successfully!")
            break
        
        # Let coordinator analyze and decide using LLM
        decision = coordinator.analyze(shared)
        logger.info(f"LLM Decision: {decision.action.value}")
        logger.info(f"LLM Reasoning: {decision.reasoning}")
        logger.info(f"LLM Confidence: {decision.confidence}")
        
        # Execute the decision
        result = coordinator.execute(decision.action, shared, decision.parameters)
        
        if result.get("success"):
            logger.info(f"✅ Action executed successfully: {decision.action.value}")
            workflow_steps.append({
                "iteration": iteration + 1,
                "agent": status['current_agent'],
                "action": decision.action.value,
                "reasoning": decision.reasoning,
                "confidence": decision.confidence,
                "result": "success"
            })
        else:
            logger.error(f"❌ Action failed: {result.get('error')}")
            workflow_steps.append({
                "iteration": iteration + 1,
                "agent": status['current_agent'],
                "action": decision.action.value,
                "reasoning": decision.reasoning,
                "confidence": decision.confidence,
                "result": "failed",
                "error": result.get("error")
            })
            break
        
        # Add decision to coordinator history
        coordinator.add_to_history(decision)
    
    else:
        logger.warning("⚠️ Max iterations reached, workflow may not be complete")
    
    return {
        "success": status['task_complete'],
        "workflow_steps": workflow_steps,
        "final_status": status
    }


def test_llm_research_then_generate():
    """Test the LLM-enhanced research-then-generate workflow."""
    logger = get_logger("LLMResearchThenGenerate")
    
    logger.info("\n=== Testing LLM-Enhanced Research-Then-Generate Workflow ===")
    
    # Set up LLM-enhanced agentic system
    coordinator = setup_llm_agentic_system()
    
    # Create shared state for research-then-generate request
    shared = SharedState(
        user="researcher@example.com",
        flow_type=FlowType.TOKENED_USER,
        email={
            "id": "llm_research_generate_1",
            "from": "researcher@example.com",
            "to": "assistant@example.com",
            "subject": "Research and generate content",
            "body": "Please research the latest developments in artificial intelligence and then generate a song based on your findings.",
            "thread_id": "llm_research_thread_1"
        }
    )
    
    # Run the workflow
    result = run_llm_agentic_workflow(coordinator, shared)
    
    # Print workflow steps
    logger.info("\n📋 LLM-Enhanced Workflow Steps:")
    for step in result["workflow_steps"]:
        status_emoji = "✅" if step["result"] == "success" else "❌"
        logger.info(f"{status_emoji} Step {step['iteration']}: {step['agent']} - {step['action']}")
        logger.info(f"   LLM Reasoning: {step['reasoning']}")
        logger.info(f"   LLM Confidence: {step['confidence']}")
        if step.get("error"):
            logger.error(f"   Error: {step['error']}")
    
    # Print final status
    logger.info(f"\n🎯 Final Status:")
    logger.info(f"Success: {result['success']}")
    logger.info(f"Current Agent: {result['final_status']['current_agent']}")
    logger.info(f"Task Complete: {result['final_status']['task_complete']}")
    
    return result


def test_llm_ambiguous_request():
    """Test LLM handling of ambiguous requests."""
    logger = get_logger("LLMAmbiguousRequest")
    
    logger.info("\n=== Testing LLM Handling of Ambiguous Requests ===")
    
    # Set up LLM-enhanced agentic system
    coordinator = setup_llm_agentic_system()
    
    # Create shared state for ambiguous request
    shared = SharedState(
        user="user@example.com",
        flow_type=FlowType.TOKENED_USER,
        email={
            "id": "ambiguous_1",
            "from": "user@example.com",
            "to": "assistant@example.com",
            "subject": "Help me with this",
            "body": "I need information about climate change and want something creative about it.",
            "thread_id": "ambiguous_thread_1"
        }
    )
    
    # Run the workflow
    result = run_llm_agentic_workflow(coordinator, shared)
    
    logger.info(f"\n🎯 Ambiguous Request Result:")
    logger.info(f"Success: {result['success']}")
    logger.info(f"Final Agent: {result['final_status']['current_agent']}")
    logger.info(f"Steps: {len(result['workflow_steps'])}")
    
    return result


def test_llm_complex_request():
    """Test LLM handling of complex multi-step requests."""
    logger = get_logger("LLMComplexRequest")
    
    logger.info("\n=== Testing LLM Handling of Complex Requests ===")
    
    # Set up LLM-enhanced agentic system
    coordinator = setup_llm_agentic_system()
    
    # Create shared state for complex request
    shared = SharedState(
        user="complex@example.com",
        flow_type=FlowType.TOKENED_USER,
        email={
            "id": "complex_1",
            "from": "complex@example.com",
            "to": "assistant@example.com",
            "subject": "Multi-step request",
            "body": "I want to understand the current state of renewable energy, then create a document summarizing the findings, and finally generate a song inspired by the environmental impact.",
            "thread_id": "complex_thread_1"
        }
    )
    
    # Run the workflow
    result = run_llm_agentic_workflow(coordinator, shared)
    
    logger.info(f"\n🎯 Complex Request Result:")
    logger.info(f"Success: {result['success']}")
    logger.info(f"Final Agent: {result['final_status']['current_agent']}")
    logger.info(f"Steps: {len(result['workflow_steps'])}")
    
    return result


def test_llm_tokenless_user():
    """Test LLM handling of tokenless user requests."""
    logger = get_logger("LLMTokenlessUser")
    
    logger.info("\n=== Testing LLM Handling of Tokenless User Requests ===")
    
    # Set up LLM-enhanced agentic system
    coordinator = setup_llm_agentic_system()
    
    # Create shared state for tokenless user
    shared = SharedState(
        user="newuser@example.com",
        flow_type=FlowType.TOKENLESS_USER,
        email={
            "id": "llm_tokenless_1",
            "from": "newuser@example.com",
            "to": "assistant@example.com",
            "subject": "I want to generate content",
            "body": "Please generate a song for me.",
            "thread_id": "llm_tokenless_thread_1"
        }
    )
    
    # Run the workflow
    result = run_llm_agentic_workflow(coordinator, shared)
    
    logger.info(f"\n🎯 LLM Tokenless User Result:")
    logger.info(f"Success: {result['success']}")
    logger.info(f"Final Agent: {result['final_status']['current_agent']}")
    
    return result


def compare_llm_vs_keyword_approaches():
    """Compare LLM-enhanced vs keyword-based approaches."""
    logger = get_logger("LLMComparison")
    
    logger.info("\n=== Comparing LLM vs Keyword Approaches ===")
    
    # Test cases
    test_cases = [
        {
            "name": "Clear Research Request",
            "body": "Research the latest developments in quantum computing."
        },
        {
            "name": "Clear Content Request", 
            "body": "Generate a song in the style of Daft Punk."
        },
        {
            "name": "Ambiguous Request",
            "body": "I need information about climate change and want something creative about it."
        },
        {
            "name": "Complex Multi-step Request",
            "body": "Research renewable energy, create a summary document, and generate a song about environmental impact."
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        logger.info(f"\n--- Testing: {test_case['name']} ---")
        logger.info(f"Request: {test_case['body']}")
        
        # Set up LLM-enhanced system
        coordinator = setup_llm_agentic_system()
        
        # Create shared state
        shared = SharedState(
            user="test@example.com",
            flow_type=FlowType.TOKENED_USER,
            email={
                "id": f"test_{test_case['name'].lower().replace(' ', '_')}",
                "from": "test@example.com",
                "to": "assistant@example.com",
                "subject": test_case['name'],
                "body": test_case['body'],
                "thread_id": f"test_thread_{test_case['name'].lower().replace(' ', '_')}"
            }
        )
        
        # Run workflow
        result = run_llm_agentic_workflow(coordinator, shared)
        
        results[test_case['name']] = {
            "success": result['success'],
            "steps": len(result['workflow_steps']),
            "final_agent": result['final_status']['current_agent'],
            "workflow_steps": result['workflow_steps']
        }
    
    # Print comparison summary
    logger.info("\n" + "="*60)
    logger.info("📊 LLM vs Keyword Approach Comparison")
    logger.info("="*60)
    
    for test_name, result in results.items():
        status_emoji = "✅" if result["success"] else "❌"
        logger.info(f"{status_emoji} {test_name}:")
        logger.info(f"   Success: {result['success']}")
        logger.info(f"   Steps: {result['steps']}")
        logger.info(f"   Final Agent: {result['final_agent']}")
    
    logger.info("="*60)
    
    return results


def main():
    """Run all LLM-enhanced agentic workflow tests."""
    # Set up logging
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("LLMAgenticExample")
    
    logger.info("🚀 Starting LLM-Enhanced Agentic PocketFlow Examples")
    
    # Test different workflows
    results = {}
    
    # Test 1: LLM research then generate
    results["llm_research_then_generate"] = test_llm_research_then_generate()
    
    # Test 2: LLM ambiguous request
    results["llm_ambiguous_request"] = test_llm_ambiguous_request()
    
    # Test 3: LLM complex request
    results["llm_complex_request"] = test_llm_complex_request()
    
    # Test 4: LLM tokenless user
    results["llm_tokenless_user"] = test_llm_tokenless_user()
    
    # Test 5: Comparison
    results["llm_comparison"] = compare_llm_vs_keyword_approaches()
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("📊 LLM-ENHANCED AGENTIC WORKFLOW RESULTS SUMMARY")
    logger.info("="*60)
    
    for test_name, result in results.items():
        if test_name == "llm_comparison":
            logger.info(f"📊 {test_name}: Comparison completed")
        else:
            status_emoji = "✅" if result["success"] else "❌"
            logger.info(f"{status_emoji} {test_name}: {result['success']}")
            logger.info(f"   Steps: {len(result['workflow_steps'])}")
            logger.info(f"   Final Agent: {result['final_status']['current_agent']}")
    
    logger.info("="*60)
    logger.info("🎉 LLM-enhanced agentic workflow examples completed!")
    
    return results


if __name__ == "__main__":
    main() 