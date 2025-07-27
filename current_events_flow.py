from pocketflow import Flow
from current_events_nodes import (
    FetchCurrentEventsNode,
    ProcessEventsNode,
    GenerateWorldOverviewNode,
    FormatFinalReportNode
)

def create_current_events_flow():
    """
    Create a flow for generating current events overview
    
    Flow:
    1. Fetch current events from bubb.la
    2. Process and structure the raw data
    3. Generate comprehensive world overview
    4. Format final report for presentation
    """
    
    # Create nodes
    fetch_events = FetchCurrentEventsNode(max_retries=3, wait=5)
    process_events = ProcessEventsNode(max_retries=2, wait=3)
    generate_overview = GenerateWorldOverviewNode(max_retries=2, wait=3)
    format_report = FormatFinalReportNode()
    
    # Connect nodes in sequence
    fetch_events >> process_events >> generate_overview >> format_report
    
    # Create and return the flow
    return Flow(start=fetch_events)

def run_current_events_overview():
    """
    Run the current events overview flow
    
    Returns:
        The shared state containing the final report
    """
    # Initialize shared store
    shared = {
        "raw_events_data": None,
        "processed_events": None,
        "world_overview": None,
        "final_report": None
    }
    
    # Create and run the flow
    flow = create_current_events_flow()
    flow.run(shared)
    
    return shared

if __name__ == "__main__":
    # Run the current events overview
    print("Starting Current Events Overview...")
    print("Fetching data from http://bubb.la...")
    
    result = run_current_events_overview()
    
    print("\nFlow completed!")
    print(f"Final report available in result['final_report']") 