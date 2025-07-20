"""
Complete Agentic PocketFlow Example

This example demonstrates the complete agentic architecture with both
traditional keyword-based and LLM-enhanced approaches.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pocketflow import SharedState, FlowType, setup_logging, get_logger
from pocketflow.agents import (
    # Traditional agents
    CoordinatorAgent, ResearchAgent, ContentAgent, EmailAgent, PaymentAgent,
    # LLM-enhanced agents
    LLMEnhancedCoordinatorAgent, LLMEnhancedResearchAgent
)
from pocketflow.agents.base_agent import AgentAction


def setup_traditional_agentic_system():
    """Set up the traditional keyword-based agentic system."""
    logger = get_logger("TraditionalAgenticExample")
    
    # Create traditional coordinator agent
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
    
    logger.info("Traditional keyword-based agentic system set up")
    
    return coordinator


def setup_llm_enhanced_agentic_system():
    """Set up the LLM-enhanced agentic system."""
    logger = get_logger("LLMAgenticExample")
    
    # Create LLM-enhanced coordinator agent
    coordinator = LLMEnhancedCoordinatorAgent()
    
    # Create specialized agents (mix of traditional and LLM-enhanced)
    research_agent = LLMEnhancedResearchAgent()
    content_agent = ContentAgent()
    email_agent = EmailAgent()
    payment_agent = PaymentAgent()
    
    # Register agents with coordinator
    coordinator.register_agent(research_agent)
    coordinator.register_agent(content_agent)
    coordinator.register_agent(email_agent)
    coordinator.register_agent(payment_agent)
    
    logger.info("LLM-enhanced agentic system set up")
    
    return coordinator


def run_agentic_workflow(coordinator, shared: SharedState, system_name: str):
    """Run the agentic workflow."""
    logger = get_logger(f"{system_name}Workflow")
    
    logger.info(f"🚀 Starting {system_name} agentic workflow")
    
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


def compare_approaches():
    """Compare traditional vs LLM-enhanced approaches."""
    logger = get_logger("ApproachComparison")
    
    logger.info("\n=== Comparing Traditional vs LLM-Enhanced Approaches ===")
    
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
        },
        {
            "name": "Mixed Intent Request",
            "body": "Can you help me understand AI trends and maybe create something interesting about it?"
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        logger.info(f"\n--- Testing: {test_case['name']} ---")
        logger.info(f"Request: {test_case['body']}")
        
        # Test traditional approach
        traditional_coordinator = setup_traditional_agentic_system()
        traditional_shared = SharedState(
            user="test@example.com",
            flow_type=FlowType.TOKENED_USER,
            email={
                "id": f"traditional_{test_case['name'].lower().replace(' ', '_')}",
                "from": "test@example.com",
                "to": "assistant@example.com",
                "subject": test_case['name'],
                "body": test_case['body'],
                "thread_id": f"traditional_thread_{test_case['name'].lower().replace(' ', '_')}"
            }
        )
        
        traditional_result = run_agentic_workflow(traditional_coordinator, traditional_shared, "Traditional")
        
        # Test LLM-enhanced approach
        llm_coordinator = setup_llm_enhanced_agentic_system()
        llm_shared = SharedState(
            user="test@example.com",
            flow_type=FlowType.TOKENED_USER,
            email={
                "id": f"llm_{test_case['name'].lower().replace(' ', '_')}",
                "from": "test@example.com",
                "to": "assistant@example.com",
                "subject": test_case['name'],
                "body": test_case['body'],
                "thread_id": f"llm_thread_{test_case['name'].lower().replace(' ', '_')}"
            }
        )
        
        llm_result = run_agentic_workflow(llm_coordinator, llm_shared, "LLM-Enhanced")
        
        # Store comparison results
        results[test_case['name']] = {
            "traditional": {
                "success": traditional_result['success'],
                "steps": len(traditional_result['workflow_steps']),
                "final_agent": traditional_result['final_status']['current_agent'],
                "workflow_steps": traditional_result['workflow_steps']
            },
            "llm_enhanced": {
                "success": llm_result['success'],
                "steps": len(llm_result['workflow_steps']),
                "final_agent": llm_result['final_status']['current_agent'],
                "workflow_steps": llm_result['workflow_steps']
            }
        }
    
    # Print comparison summary
    logger.info("\n" + "="*80)
    logger.info("📊 TRADITIONAL vs LLM-ENHANCED APPROACH COMPARISON")
    logger.info("="*80)
    
    for test_name, result in results.items():
        logger.info(f"\n🔍 {test_name}:")
        
        # Traditional results
        trad_status = "✅" if result["traditional"]["success"] else "❌"
        logger.info(f"   Traditional: {trad_status}")
        logger.info(f"     Success: {result['traditional']['success']}")
        logger.info(f"     Steps: {result['traditional']['steps']}")
        logger.info(f"     Final Agent: {result['traditional']['final_agent']}")
        
        # LLM-enhanced results
        llm_status = "✅" if result["llm_enhanced"]["success"] else "❌"
        logger.info(f"   LLM-Enhanced: {llm_status}")
        logger.info(f"     Success: {result['llm_enhanced']['success']}")
        logger.info(f"     Steps: {result['llm_enhanced']['steps']}")
        logger.info(f"     Final Agent: {result['llm_enhanced']['final_agent']}")
        
        # Compare reasoning quality
        if result["traditional"]["workflow_steps"] and result["llm_enhanced"]["workflow_steps"]:
            trad_reasoning = result["traditional"]["workflow_steps"][0].get("reasoning", "")
            llm_reasoning = result["llm_enhanced"]["workflow_steps"][0].get("reasoning", "")
            logger.info(f"     Traditional Reasoning: {trad_reasoning[:50]}...")
            logger.info(f"     LLM Reasoning: {llm_reasoning[:50]}...")
    
    logger.info("="*80)
    
    return results


def demonstrate_agent_capabilities():
    """Demonstrate the capabilities of different agents."""
    logger = get_logger("AgentCapabilities")
    
    logger.info("\n=== Demonstrating Agent Capabilities ===")
    
    # Create agents
    agents = {
        "CoordinatorAgent": CoordinatorAgent(),
        "LLMEnhancedCoordinatorAgent": LLMEnhancedCoordinatorAgent(),
        "ResearchAgent": ResearchAgent(),
        "LLMEnhancedResearchAgent": LLMEnhancedResearchAgent(),
        "ContentAgent": ContentAgent(),
        "EmailAgent": EmailAgent(),
        "PaymentAgent": PaymentAgent()
    }
    
    # Display capabilities
    for agent_name, agent in agents.items():
        logger.info(f"\n🤖 {agent_name}:")
        capabilities = agent.get_capabilities()
        for capability in capabilities:
            logger.info(f"   - {capability}")
        
        # Get agent info
        agent_info = agent.get_agent_info()
        logger.info(f"   Context: {len(agent_info['context'])} items")
        logger.info(f"   History: {agent_info['history_length']} decisions")
    
    return agents


def test_specific_workflows():
    """Test specific workflow scenarios."""
    logger = get_logger("SpecificWorkflows")
    
    logger.info("\n=== Testing Specific Workflow Scenarios ===")
    
    workflows = [
        {
            "name": "Research-Then-Generate (Traditional)",
            "body": "Research AI developments and generate a song about it.",
            "system": "traditional"
        },
        {
            "name": "Research-Then-Generate (LLM-Enhanced)",
            "body": "Research AI developments and generate a song about it.",
            "system": "llm_enhanced"
        },
        {
            "name": "Direct Content Generation (Traditional)",
            "body": "Generate a song about space exploration.",
            "system": "traditional"
        },
        {
            "name": "Direct Content Generation (LLM-Enhanced)",
            "body": "Generate a song about space exploration.",
            "system": "llm_enhanced"
        },
        {
            "name": "Tokenless User (Traditional)",
            "body": "I want to generate content.",
            "system": "traditional",
            "flow_type": FlowType.TOKENLESS_USER
        },
        {
            "name": "Tokenless User (LLM-Enhanced)",
            "body": "I want to generate content.",
            "system": "llm_enhanced",
            "flow_type": FlowType.TOKENLESS_USER
        }
    ]
    
    results = {}
    
    for workflow in workflows:
        logger.info(f"\n--- Testing: {workflow['name']} ---")
        logger.info(f"Request: {workflow['body']}")
        
        # Set up appropriate system
        if workflow['system'] == 'traditional':
            coordinator = setup_traditional_agentic_system()
        else:
            coordinator = setup_llm_enhanced_agentic_system()
        
        # Create shared state
        flow_type = workflow.get('flow_type', FlowType.TOKENED_USER)
        shared = SharedState(
            user="test@example.com",
            flow_type=flow_type,
            email={
                "id": f"workflow_{workflow['name'].lower().replace(' ', '_').replace('(', '').replace(')', '')}",
                "from": "test@example.com",
                "to": "assistant@example.com",
                "subject": workflow['name'],
                "body": workflow['body'],
                "thread_id": f"workflow_thread_{workflow['name'].lower().replace(' ', '_').replace('(', '').replace(')', '')}"
            }
        )
        
        # Run workflow
        result = run_agentic_workflow(coordinator, shared, workflow['system'].title())
        
        results[workflow['name']] = {
            "success": result['success'],
            "steps": len(result['workflow_steps']),
            "final_agent": result['final_status']['current_agent'],
            "workflow_steps": result['workflow_steps']
        }
    
    # Print workflow results
    logger.info("\n" + "="*60)
    logger.info("📋 SPECIFIC WORKFLOW RESULTS")
    logger.info("="*60)
    
    for workflow_name, result in results.items():
        status_emoji = "✅" if result["success"] else "❌"
        logger.info(f"{status_emoji} {workflow_name}:")
        logger.info(f"   Success: {result['success']}")
        logger.info(f"   Steps: {result['steps']}")
        logger.info(f"   Final Agent: {result['final_agent']}")
    
    logger.info("="*60)
    
    return results


def main():
    """Run the complete agentic example."""
    # Set up logging
    setup_logging(level="INFO", log_format="standard")
    logger = get_logger("CompleteAgenticExample")
    
    logger.info("🚀 Starting Complete Agentic PocketFlow Example")
    
    # Run all demonstrations
    results = {}
    
    # 1. Demonstrate agent capabilities
    results["agent_capabilities"] = demonstrate_agent_capabilities()
    
    # 2. Compare approaches
    results["approach_comparison"] = compare_approaches()
    
    # 3. Test specific workflows
    results["specific_workflows"] = test_specific_workflows()
    
    # Print final summary
    logger.info("\n" + "="*80)
    logger.info("🎉 COMPLETE AGENTIC EXAMPLE SUMMARY")
    logger.info("="*80)
    
    logger.info(f"📊 Agent Capabilities: {len(results['agent_capabilities'])} agents demonstrated")
    logger.info(f"📊 Approach Comparison: {len(results['approach_comparison'])} test cases compared")
    logger.info(f"📊 Specific Workflows: {len(results['specific_workflows'])} workflows tested")
    
    # Calculate success rates
    approach_success = sum(1 for result in results['approach_comparison'].values() 
                          if result['traditional']['success'] or result['llm_enhanced']['success'])
    workflow_success = sum(1 for result in results['specific_workflows'].values() 
                          if result['success'])
    
    logger.info(f"📈 Approach Comparison Success Rate: {approach_success}/{len(results['approach_comparison'])}")
    logger.info(f"📈 Specific Workflow Success Rate: {workflow_success}/{len(results['specific_workflows'])}")
    
    logger.info("="*80)
    logger.info("🎯 Complete agentic example finished!")
    
    return results


if __name__ == "__main__":
    main() 