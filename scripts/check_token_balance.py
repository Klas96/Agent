import sys
import os
sys.path.append('/opt/pocketflow')

from src.pocketflow.services import database_service

def main():
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = input("Enter email address to check: ")
    
    if not email:
        print("Email address is required.")
        sys.exit(1)
    
    tokens = database_service.get_tokens(email)
    print(f"Token balance for {email}: {tokens}")

if __name__ == "__main__":
    main() 