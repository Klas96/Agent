"""
Agentic PocketFlow Example

This example demonstrates the agentic approach where agents dynamically
decide what actions to take based on context, including the research-then-generate workflow.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pocketflow import SharedState, FlowType, setup_logging, get_logger
from pocketflow.agents import (
    CoordinatorAgent, ResearchAgent, ContentAgent, 
    EmailAgent, PaymentAgent
)
from pocketflow.agents.base_agent import AgentAction


def setup_agentic_system():
    """Set up the agentic system with all agents."""
    logger = get_logger("AgenticExample")
    
    # Create coordinator agent
    coordinator = CoordinatorAgent()
    
    # Create specialized agents
    research_agent = ResearchAgent()
    content_agent = ContentAgent()
    email_agent = EmailAgent()
    payment_agent = PaymentAgent()
    
    # Register agents with coordinator
    coordinator.register_agent(research_agent)
    coordinator.register_agent(content_agent)
    coordinator.register_agent(email_agent)
    coordinator.register_agent(payment_agent)
    
    logger.info("Agentic system set up with all agents registered")
    
    return coordinator


def run_agentic_workflow(coordinator, shared: SharedState):
    """Run the agentic workflow."""
    logger = get_logger("AgenticWorkflow")
    
    logger.info("🚀 Starting agentic workflow")
    
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
        
        # Let coordinator analyze and decide
        decision = coordinator.analyze(shared)
        logger.info(f"Decision: {decision.action.value}")
        logger.info(f"Reasoning: {decision.reasoning}")
        logger.info(f"Confidence: {decision.confidence}")
        
        # Execute the decision
        result = coordinator.execute(decision.action, shared, decision.parameters)
        
        if result.get("success"):
            logger.info(f"✅ Action executed successfully: {decision.action.value}")
            workflow_steps.append({
                "iteration": iteration + 1,
                "agent": status['current_agent'],
                "action": decision.action.value,
                "reasoning": decision.reasoning,
                "result": "success"
            })
        else:
            logger.error(f"❌ Action failed: {result.get('error')}")
            workflow_steps.append({
                "iteration": iteration + 1,
                "agent": status['current_agent'],
                "action": decision.action.value,
                "reasoning": decision.reasoning,
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


def test_research_then_generate():
    """Test the research-then-generate workflow."""
    logger = get_logger("ResearchThenGenerate")
    
    logger.info("\n=== Testing Research-Then-Generate Workflow ===")
    
    # Set up agentic system
    coordinator = setup_agentic_system()
    
    # Create shared state for research-then-generate request
    shared = SharedState(
        user="researcher@example.com",
        flow_type=FlowType.TOKENED_USER,
        email={
            "id": "research_generate_1",
            "from": "researcher@example.com",
            "to": "assistant@example.com",
            "subject": "Research and generate content",
            "body": "Please research the latest developments in artificial intelligence and then generate a song based on your findings.",
            "thread_id": "research_thread_1"
        }
    )
    
    # Run the workflow
    result = run_agentic_workflow(coordinator, shared)
    
    # Print workflow steps
    logger.info("\n📋 Workflow Steps:")
    for step in result["workflow_steps"]:
        status_emoji = "✅" if step["result"] == "success" else "❌"
        logger.info(f"{status_emoji} Step {step['iteration']}: {step['agent']} - {step['action']}")
        logger.info(f"   Reasoning: {step['reasoning']}")
        if step.get("error"):
            logger.error(f"   Error: {step['error']}")
    
    # Print final status
    logger.info(f"\n🎯 Final Status:")
    logger.info(f"Success: {result['success']}")
    logger.info(f"Current Agent: {result['final_status']['current_agent']}")
    logger.info(f"Task Complete: {result['final_status']['task_complete']}")
    
    return result


def test_tokenless_user():
    """Test tokenless user workflow."""
    logger = get_logger("TokenlessUser")
    
    logger.info("\n=== Testing Tokenless User Workflow ===")
    
    # Set up agentic system
    coordinator = setup_agentic_system()
    
    # Create shared state for tokenless user
    shared = SharedState(
        user="newuser@example.com",
        flow_type=FlowType.TOKENLESS_USER,
        email={
            "id": "tokenless_1",
            "from": "newuser@example.com",
            "to": "assistant@example.com",
            "subject": "I want to generate content",
            "body": "Please generate a song for me.",
            "thread_id": "tokenless_thread_1"
        }
    )
    
    # Run the workflow
    result = run_agentic_workflow(coordinator, shared)
    
    logger.info(f"\n🎯 Tokenless User Result:")
    logger.info(f"Success: {result['success']}")
    logger.info(f"Final Agent: {result['final_status']['current_agent']}")
    
    return result


def test_direct_content_generation():
    """Test direct content generation without research."""
    logger = get_logger("DirectContent")
    
    logger.info("\n=== Testing Direct Content Generation ===")
    
    # Set up agentic system
    coordinator = setup_agentic_system()
    
    # Create shared state for direct content generation
    shared = SharedState(
        user="creator@example.com",
        flow_type=FlowType.TOKENED_USER,
        email={
            "id": "direct_content_1",
            "from": "creator@example.com",
            "to": "assistant@example.com",
            "subject": "Generate a song",
            "body": "Please generate a 2-minute song in the style of Daft Punk.",
            "thread_id": "direct_thread_1"
        }
    )
    
    # Run the workflow
    result = run_agentic_workflow(coordinator, shared)
    
    logger.info(f"\n🎯 Direct Content Generation Result:")
    logger.info(f"Success: {result['success']}")
    logger.info(f"Final Agent: {result['final_status']['current_agent']}")
    
    return result


def test_pure_research():
    """Test pure research without content generation."""
    logger = get_logger("PureResearch")
    
    logger.info("\n=== Testing Pure Research Workflow ===")
    
    # Set up agentic system
    coordinator = setup_agentic_system()
    
    # Create shared state for pure research
    shared = SharedState(
        user="researcher@example.com",
        flow_type=FlowType.TOKENED_USER,
        email={
            "id": "pure_research_1",
            "from": "researcher@example.com",
            "to": "assistant@example.com",
            "subject": "Research request",
            "body": "Please research the latest developments in quantum computing.",
            "thread_id": "pure_research_thread_1"
        }
    )
    
    # Run the workflow
    result = run_agentic_workflow(coordinator, shared)
    
    logger.info(f"\n🎯 Pure Research Result:")
    logger.info(f"Success: {result['success']}")
    logger.info(f"Final Agent: {result['final_status']['current_agent']}")
    
    return result


def main():
    """Run all agentic workflow tests."""
    # Set up logging
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("AgenticExample")
    
    logger.info("🚀 Starting Agentic PocketFlow Examples")
    
    # Test different workflows
    results = {}
    
    # Test 1: Research then generate
    results["research_then_generate"] = test_research_then_generate()
    
    # Test 2: Tokenless user
    results["tokenless_user"] = test_tokenless_user()
    
    # Test 3: Direct content generation
    results["direct_content"] = test_direct_content_generation()
    
    # Test 4: Pure research
    results["pure_research"] = test_pure_research()
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("📊 AGENTIC WORKFLOW RESULTS SUMMARY")
    logger.info("="*60)
    
    for test_name, result in results.items():
        status_emoji = "✅" if result["success"] else "❌"
        logger.info(f"{status_emoji} {test_name}: {result['success']}")
        logger.info(f"   Steps: {len(result['workflow_steps'])}")
        logger.info(f"   Final Agent: {result['final_status']['current_agent']}")
    
    logger.info("="*60)
    logger.info("🎉 Agentic workflow examples completed!")
    
    return results


if __name__ == "__main__":
    main() 