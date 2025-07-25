import os
import logging
import time
from src.pocketflow.core.types import SharedState
from src.pocketflow.utils.logging import setup_logging, get_logger
from src.pocketflow.config.settings import get_settings
from src.pocketflow.flows.manager import flow_manager

print("=== MAIN.PY IS BEING EXECUTED ===")

# Configure logging to show INFO level messages
setup_logging(level="INFO", log_format="standard")

def main():
    logger = get_logger("main")
    logger.info("=== MAIN FUNCTION STARTED ===")
    
    shared = SharedState()
    logger.info("=== SharedState created ===")
    
    iteration = 0
    while True:
        iteration += 1
        logger.info(f"=== Starting iteration {iteration} ===")
        try:
            # Use the flow manager to automatically select and run the appropriate flow
            result = flow_manager.run_auto_select(shared)
            logger.info(f"=== Flow run completed for iteration {iteration}, result: {result} ===")
        except Exception as e:
            logger.error(f"=== Flow run failed for iteration {iteration}: {e} ===", exc_info=True)
        
        logger.info(f"=== Sleeping for 10 seconds after iteration {iteration} ===")
        time.sleep(10)  # Poll every 10 seconds

if __name__ == "__main__":
    main() 