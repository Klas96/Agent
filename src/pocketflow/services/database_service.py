"""
Database service for PocketFlow.

This module provides database operations for user management and BTC addresses.
Supports both SQLite and PostgreSQL databases.
"""

import os
import sqlite3
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

from ..core.types import User, BTCAddress, DonationTransaction
from ..config.settings import get_settings
from ..utils.errors import DatabaseError
from ..utils.logging import get_logger


class DatabaseService:
    """Service for handling database operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("DatabaseService")
        self.db_type = self._get_db_type()
        self.db_path = self._get_db_path()
        self._init_database()
    
    def _get_db_type(self) -> str:
        """Determine database type from DATABASE_URL."""
        if hasattr(self.settings, 'DATABASE_URL') and self.settings.DATABASE_URL:
            if self.settings.DATABASE_URL.startswith('postgresql://'):
                return 'postgresql'
            elif self.settings.DATABASE_URL.startswith('sqlite:///'):
                return 'sqlite'
        
        # Default to PostgreSQL if available, otherwise SQLite
        if POSTGRESQL_AVAILABLE:
            return 'postgresql'
        return 'sqlite'
    
    def _get_db_path(self) -> str:
        """Get the database connection string or file path."""
        if hasattr(self.settings, 'DATABASE_URL') and self.settings.DATABASE_URL:
            return self.settings.DATABASE_URL
        
        # Default connection strings
        if self.db_type == 'postgresql':
            return "postgresql://pocketflow:pocketflow_password@localhost:5432/pocketflow"
        else:
            # Use absolute path for production
            data_dir = Path("/opt/pocketflow/data")
            data_dir.mkdir(exist_ok=True)
            return str(data_dir / "pocketflow.db")
    
    def _get_connection(self):
        """Get database connection based on type."""
        if self.db_type == 'postgresql':
            return psycopg2.connect(self.db_path)
        else:
            return sqlite3.connect(self.db_path)
    
    def _init_database(self):
        """Initialize the database with required tables."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if tables already exist
            if self.db_type == 'postgresql':
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'users'
                    );
                """)
                tables_exist = cursor.fetchone()[0]
            else:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='users';
                """)
                tables_exist = cursor.fetchone() is not None
            
            if not tables_exist:
                if self.db_type == 'postgresql':
                    # Create users table for PostgreSQL
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            email VARCHAR(255) UNIQUE NOT NULL,
                            name VARCHAR(255),
                            personality TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # Create scheduled_jobs table for PostgreSQL
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS scheduled_jobs (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            description TEXT,
                            job_type VARCHAR(100) NOT NULL,
                            schedule VARCHAR(100) NOT NULL,
                            flow_config TEXT,
                            is_active BOOLEAN DEFAULT TRUE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # Create job_executions table for PostgreSQL
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS job_executions (
                            id SERIAL PRIMARY KEY,
                            job_id INTEGER REFERENCES scheduled_jobs(id),
                            status VARCHAR(50) NOT NULL,
                            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            completed_at TIMESTAMP,
                            result TEXT,
                            error_message TEXT
                        )
                    ''')
                else:
                    # Create users table for SQLite
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            email TEXT UNIQUE NOT NULL,
                            name TEXT,
                            personality TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # Create scheduled_jobs table for SQLite
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS scheduled_jobs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            description TEXT,
                            job_type TEXT NOT NULL,
                            schedule TEXT NOT NULL,
                            flow_config TEXT,
                            is_active BOOLEAN DEFAULT 1,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # Create job_executions table for SQLite
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS job_executions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            job_id INTEGER,
                            status TEXT NOT NULL,
                            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            completed_at TIMESTAMP,
                            result TEXT,
                            error_message TEXT,
                            FOREIGN KEY (job_id) REFERENCES scheduled_jobs (id)
                        )
                    ''')
            
            conn.commit()
            conn.close()
            self.logger.info(f"Database initialized at {self.db_path} (Type: {self.db_type})")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")
    
    def get_user(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT email, name, personality, created_at, updated_at 
                FROM users WHERE email = %s
            ''' if self.db_type == 'postgresql' else '''
                SELECT email, name, personality, created_at, updated_at 
                FROM users WHERE email = ?
            ''', (email,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                            return User(
                email=result[0],
                name=result[1],
                personality=result[2],
                created_at=result[3],
                updated_at=result[4]
            )
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get user {email}: {e}")
            raise DatabaseError(f"Failed to get user: {e}")
    
    def get_all_users(self) -> List[Dict]:
        """Get all users with their information."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT email, name, personality, created_at, updated_at 
                FROM users ORDER BY created_at DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            users = []
            for result in results:
                users.append({
                    'email': result[0],
                    'name': result[1],
                    'personality': result[2],
                    'created_at': result[3],
                    'updated_at': result[4]
                })
            
            return users
            
        except Exception as e:
            self.logger.error(f"Failed to get all users: {e}")
            raise DatabaseError(f"Failed to get all users: {e}")
    
    def create_user(self, email: str, name: Optional[str] = None, personality: Optional[str] = None) -> User:
        """Create a new user."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (email, name, personality) 
                VALUES (%s, %s, %s)
            ''' if self.db_type == 'postgresql' else '''
                INSERT INTO users (email, name, personality) 
                VALUES (?, ?, ?)
            ''', (email, name, personality))
            
            conn.commit()
            conn.close()
            
            return User(
                email=email,
                name=name,
                personality=personality,
                created_at=None,
                updated_at=None
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create user {email}: {e}")
            raise DatabaseError(f"Failed to create user: {e}")
    
    def update_user_personality(self, email: str, personality: Optional[str] = None) -> bool:
        """Update user personality."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET personality = %s, updated_at = CURRENT_TIMESTAMP 
                WHERE email = %s
            ''' if self.db_type == 'postgresql' else '''
                UPDATE users SET personality = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE email = ?
            ''', (personality, email))
            
            conn.commit()
            conn.close()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Failed to update user {email}: {e}")
            raise DatabaseError(f"Failed to update user: {e}")
    
    def delete_user(self, email: str) -> bool:
        """Delete a user."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM users WHERE email = %s
            ''' if self.db_type == 'postgresql' else '''
                DELETE FROM users WHERE email = ?
            ''', (email,))
            
            conn.commit()
            conn.close()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Failed to delete user {email}: {e}")
            raise DatabaseError(f"Failed to delete user: {e}")
    
    def get_scheduled_jobs(self) -> List[Dict]:
        """Get all scheduled jobs."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, description, job_type, schedule, flow_config, is_active, created_at, updated_at
                FROM scheduled_jobs ORDER BY created_at DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            jobs = []
            for result in results:
                jobs.append({
                    'id': result[0],
                    'name': result[1],
                    'description': result[2],
                    'job_type': result[3],
                    'schedule': result[4],
                    'flow_config': result[5],
                    'is_active': result[6],
                    'created_at': result[7],
                    'updated_at': result[8]
                })
            
            return jobs
            
        except Exception as e:
            self.logger.error(f"Failed to get scheduled jobs: {e}")
            raise DatabaseError(f"Failed to get scheduled jobs: {e}")
    
    def create_scheduled_job(self, name: str, description: str, job_type: str, schedule: str, flow_config: str) -> int:
        """Create a new scheduled job."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO scheduled_jobs (name, description, job_type, schedule, flow_config)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            ''' if self.db_type == 'postgresql' else '''
                INSERT INTO scheduled_jobs (name, description, job_type, schedule, flow_config)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, description, job_type, schedule, flow_config))
            
            if self.db_type == 'postgresql':
                job_id = cursor.fetchone()[0]
            else:
                job_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return job_id
            
        except Exception as e:
            self.logger.error(f"Failed to create scheduled job: {e}")
            raise DatabaseError(f"Failed to create scheduled job: {e}")
    
    def update_scheduled_job(self, job_id: int, **kwargs) -> bool:
        """Update a scheduled job."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['name', 'description', 'job_type', 'schedule', 'flow_config', 'is_active']:
                    set_clauses.append(f"{key} = %s" if self.db_type == 'postgresql' else f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(job_id)
            
            query = f'''
                UPDATE scheduled_jobs SET {', '.join(set_clauses)}
                WHERE id = %s
            ''' if self.db_type == 'postgresql' else f'''
                UPDATE scheduled_jobs SET {', '.join(set_clauses)}
                WHERE id = ?
            '''
            
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Failed to update scheduled job {job_id}: {e}")
            raise DatabaseError(f"Failed to update scheduled job: {e}")
    
    def delete_scheduled_job(self, job_id: int) -> bool:
        """Delete a scheduled job."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM scheduled_jobs WHERE id = %s
            ''' if self.db_type == 'postgresql' else '''
                DELETE FROM scheduled_jobs WHERE id = ?
            ''', (job_id,))
            
            conn.commit()
            conn.close()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Failed to delete scheduled job {job_id}: {e}")
            raise DatabaseError(f"Failed to delete scheduled job: {e}")
    
    def create_job_execution(self, job_id: int, status: str) -> int:
        """Create a new job execution record."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO job_executions (job_id, status)
                VALUES (%s, %s) RETURNING id
            ''' if self.db_type == 'postgresql' else '''
                INSERT INTO job_executions (job_id, status)
                VALUES (?, ?)
            ''', (job_id, status))
            
            if self.db_type == 'postgresql':
                execution_id = cursor.fetchone()[0]
            else:
                execution_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return execution_id
            
        except Exception as e:
            self.logger.error(f"Failed to create job execution: {e}")
            raise DatabaseError(f"Failed to create job execution: {e}")
    
    def update_job_execution(self, execution_id: int, status: str, result: Optional[str] = None, error_message: Optional[str] = None) -> bool:
        """Update a job execution record."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE job_executions 
                SET status = %s, completed_at = CURRENT_TIMESTAMP, result = %s, error_message = %s
                WHERE id = %s
            ''' if self.db_type == 'postgresql' else '''
                UPDATE job_executions 
                SET status = %s, completed_at = CURRENT_TIMESTAMP, result = ?, error_message = ?
                WHERE id = ?
            ''', (status, result, error_message, execution_id))
            
            conn.commit()
            conn.close()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Failed to update job execution {execution_id}: {e}")
            raise DatabaseError(f"Failed to update job execution: {e}")
    
    def get_job_executions(self, job_id: Optional[int] = None, limit: int = 50) -> List[Dict]:
        """Get job executions."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if job_id:
                cursor.execute('''
                    SELECT id, job_id, status, started_at, completed_at, result, error_message
                    FROM job_executions WHERE job_id = %s ORDER BY started_at DESC LIMIT %s
                ''' if self.db_type == 'postgresql' else '''
                    SELECT id, job_id, status, started_at, completed_at, result, error_message
                    FROM job_executions WHERE job_id = ? ORDER BY started_at DESC LIMIT ?
                ''', (job_id, limit))
            else:
                cursor.execute('''
                    SELECT id, job_id, status, started_at, completed_at, result, error_message
                    FROM job_executions ORDER BY started_at DESC LIMIT %s
                ''' if self.db_type == 'postgresql' else '''
                    SELECT id, job_id, status, started_at, completed_at, result, error_message
                    FROM job_executions ORDER BY started_at DESC LIMIT ?
                ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            executions = []
            for result in results:
                executions.append({
                    'id': result[0],
                    'job_id': result[1],
                    'status': result[2],
                    'started_at': result[3],
                    'completed_at': result[4],
                    'result': result[5],
                    'error_message': result[6]
                })
            
            return executions
            
        except Exception as e:
            self.logger.error(f"Failed to get job executions: {e}")
            raise DatabaseError(f"Failed to get job executions: {e}")
    
 