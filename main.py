import os
from flow import flow
from dotenv import load_dotenv
import time

load_dotenv()

def main():
    shared = {}
    while True:
        flow.run(shared)
        time.sleep(10)  # Poll every 10 seconds

if __name__ == "__main__":
    main() 