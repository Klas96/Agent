import os
from src.pocketflow.services import database_service

if __name__ == "__main__":
    print("Initializing database...")
    # The database is automatically initialized when DatabaseService is created
    print(f"Database schema initialized at: {database_service.db_path}") 