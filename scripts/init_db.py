import os
from utils.user_db import init_db, DB_PATH

if __name__ == "__main__":
    print("Initializing DB at:", os.path.abspath(DB_PATH))
    init_db()
    print("Database schema initialized.") 