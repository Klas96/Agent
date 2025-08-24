"""
Workflow service for PocketFlow n8n-like workflow automation platform.

This module provides database operations for workflows, executions, and logs.
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from ..core.workflow import WorkflowDefinition, ExecutionResult, ExecutionStatus
from ..config.settings import get_settings
from ..utils.logging import get_logger


class WorkflowService:
    """Service for handling workflow database operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("WorkflowService")
        self.db_path = self._get_db_path()
        self._init_database()
    
    def _get_db_path(self) -> str:
        """Get the database file path."""
        data_dir = Path("/opt/pocketflow/data")
        data_dir.mkdir(parents=True, exist_ok=True)
        return str(data_dir / "workflows.db")
    
    def _get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def _init_database(self):
        """Initialize the database with required tables."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create workflows table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflows (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    definition TEXT NOT NULL,
                    owner TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Create workflow_executions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_executions (
                    execution_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    node_results TEXT,
                    error TEXT,
                    logs TEXT,
                    initial_data TEXT,
                    FOREIGN KEY (workflow_id) REFERENCES workflows (id)
                )
            ''')
            
            # Create workflow_logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    execution_id TEXT,
                    timestamp REAL NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    data TEXT,
                    FOREIGN KEY (workflow_id) REFERENCES workflows (id),
                    FOREIGN KEY (execution_id) REFERENCES workflow_executions (execution_id)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_workflows_owner ON workflows (owner)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_workflows_active ON workflows (is_active)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_executions_workflow ON workflow_executions (workflow_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_executions_status ON workflow_executions (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_workflow ON workflow_logs (workflow_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_execution ON workflow_logs (execution_id)')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Workflow database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing workflow database: {e}")
            raise
    
    def create_workflow(self, workflow: WorkflowDefinition, owner: Optional[str] = None) -> bool:
        """Create a new workflow in the database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            workflow_json = json.dumps({
                "id": workflow.id,
                "name": workflow.name,
                "description": workflow.description,
                "nodes": [
                    {
                        "id": node.id,
                        "type": node.type,
                        "name": node.name,
                        "position": node.position,
                        "data": node.data
                    }
                    for node in workflow.nodes
                ],
                "edges": [
                    {
                        "id": edge.id,
                        "source": edge.source,
                        "target": edge.target,
                        "source_handle": edge.source_handle,
                        "target_handle": edge.target_handle,
                        "condition": edge.condition
                    }
                    for edge in workflow.edges
                ],
                "metadata": workflow.metadata,
                "created_at": workflow.created_at,
                "updated_at": workflow.updated_at
            })
            
            cursor.execute('''
                INSERT INTO workflows (id, name, description, definition, owner, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                workflow.id,
                workflow.name,
                workflow.description,
                workflow_json,
                owner,
                workflow.created_at,
                workflow.updated_at
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Workflow created: {workflow.name} (ID: {workflow.id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating workflow: {e}")
            return False
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get a workflow by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT definition FROM workflows 
                WHERE id = ? AND is_active = 1
            ''', (workflow_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                workflow_dict = json.loads(row[0])
                return self._dict_to_workflow(workflow_dict)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting workflow: {e}")
            return None
    
    def get_all_workflows(self, owner: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all workflows."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if owner:
                cursor.execute('''
                    SELECT id, name, description, owner, created_at, updated_at, is_active
                    FROM workflows 
                    WHERE owner = ? AND is_active = 1
                    ORDER BY updated_at DESC
                ''', (owner,))
            else:
                cursor.execute('''
                    SELECT id, name, description, owner, created_at, updated_at, is_active
                    FROM workflows 
                    WHERE is_active = 1
                    ORDER BY updated_at DESC
                ''')
            
            workflows = []
            for row in cursor.fetchall():
                workflows.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "owner": row[3],
                    "created_at": row[4],
                    "updated_at": row[5],
                    "is_active": bool(row[6])
                })
            
            conn.close()
            return workflows
            
        except Exception as e:
            self.logger.error(f"Error getting workflows: {e}")
            return []
    
    def update_workflow(self, workflow_id: str, workflow: WorkflowDefinition) -> bool:
        """Update a workflow."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            workflow_json = json.dumps({
                "id": workflow.id,
                "name": workflow.name,
                "description": workflow.description,
                "nodes": [
                    {
                        "id": node.id,
                        "type": node.type,
                        "name": node.name,
                        "position": node.position,
                        "data": node.data
                    }
                    for node in workflow.nodes
                ],
                "edges": [
                    {
                        "id": edge.id,
                        "source": edge.source,
                        "target": edge.target,
                        "source_handle": edge.source_handle,
                        "target_handle": edge.target_handle,
                        "condition": edge.condition
                    }
                    for edge in workflow.edges
                ],
                "metadata": workflow.metadata,
                "created_at": workflow.created_at,
                "updated_at": workflow.updated_at
            })
            
            cursor.execute('''
                UPDATE workflows 
                SET name = ?, description = ?, definition = ?, updated_at = ?
                WHERE id = ?
            ''', (
                workflow.name,
                workflow.description,
                workflow_json,
                workflow.updated_at,
                workflow_id
            ))
            
            if cursor.rowcount == 0:
                conn.close()
                return False
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Workflow updated: {workflow.name} (ID: {workflow_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating workflow: {e}")
            return False
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow (soft delete)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE workflows 
                SET is_active = 0, updated_at = ?
                WHERE id = ?
            ''', (datetime.now().timestamp(), workflow_id))
            
            if cursor.rowcount == 0:
                conn.close()
                return False
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Workflow deleted: {workflow_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting workflow: {e}")
            return False
    
    def save_execution_result(self, result: ExecutionResult) -> bool:
        """Save an execution result to the database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO workflow_executions 
                (execution_id, workflow_id, status, start_time, end_time, node_results, error, logs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.execution_id,
                result.workflow_id,
                result.status.value,
                result.start_time,
                result.end_time,
                json.dumps(result.node_results),
                result.error,
                json.dumps(result.logs)
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Execution result saved: {result.execution_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving execution result: {e}")
            return False
    
    def get_execution_result(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get an execution result by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT execution_id, workflow_id, status, start_time, end_time, 
                       node_results, error, logs
                FROM workflow_executions 
                WHERE execution_id = ?
            ''', (execution_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "execution_id": row[0],
                    "workflow_id": row[1],
                    "status": row[2],
                    "start_time": row[3],
                    "end_time": row[4],
                    "node_results": json.loads(row[5]) if row[5] else {},
                    "error": row[6],
                    "logs": json.loads(row[7]) if row[7] else []
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting execution result: {e}")
            return None
    
    def get_workflow_executions(self, workflow_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution results for a workflow."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT execution_id, status, start_time, end_time, error
                FROM workflow_executions 
                WHERE workflow_id = ?
                ORDER BY start_time DESC
                LIMIT ?
            ''', (workflow_id, limit))
            
            executions = []
            for row in cursor.fetchall():
                executions.append({
                    "execution_id": row[0],
                    "status": row[1],
                    "start_time": row[2],
                    "end_time": row[3],
                    "error": row[4]
                })
            
            conn.close()
            return executions
            
        except Exception as e:
            self.logger.error(f"Error getting workflow executions: {e}")
            return []
    
    def add_log_entry(self, workflow_id: str, level: str, message: str, 
                     execution_id: Optional[str] = None, data: Optional[Dict] = None) -> bool:
        """Add a log entry."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO workflow_logs 
                (workflow_id, execution_id, timestamp, level, message, data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                workflow_id,
                execution_id,
                datetime.now().timestamp(),
                level,
                message,
                json.dumps(data) if data else None
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding log entry: {e}")
            return False
    
    def get_workflow_logs(self, workflow_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get logs for a workflow."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, execution_id, timestamp, level, message, data
                FROM workflow_logs 
                WHERE workflow_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (workflow_id, limit))
            
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    "id": row[0],
                    "execution_id": row[1],
                    "timestamp": row[2],
                    "level": row[3],
                    "message": row[4],
                    "data": json.loads(row[5]) if row[5] else None
                })
            
            conn.close()
            return logs
            
        except Exception as e:
            self.logger.error(f"Error getting workflow logs: {e}")
            return []
    
    def _dict_to_workflow(self, workflow_dict: Dict[str, Any]) -> WorkflowDefinition:
        """Convert a dictionary to a WorkflowDefinition."""
        from ..core.workflow import NodeConfig, Edge
        
        workflow = WorkflowDefinition(
            id=workflow_dict["id"],
            name=workflow_dict["name"],
            description=workflow_dict.get("description")
        )
        
        # Add nodes
        for node_dict in workflow_dict.get("nodes", []):
            node = NodeConfig(
                id=node_dict["id"],
                type=node_dict["type"],
                name=node_dict["name"],
                position=node_dict.get("position", {}),
                data=node_dict.get("data", {})
            )
            workflow.nodes.append(node)
        
        # Add edges
        for edge_dict in workflow_dict.get("edges", []):
            edge = Edge(
                id=edge_dict["id"],
                source=edge_dict["source"],
                target=edge_dict["target"],
                source_handle=edge_dict.get("source_handle"),
                target_handle=edge_dict.get("target_handle"),
                condition=edge_dict.get("condition")
            )
            workflow.edges.append(edge)
        
        workflow.metadata = workflow_dict.get("metadata", {})
        workflow.created_at = workflow_dict.get("created_at", datetime.now().timestamp())
        workflow.updated_at = workflow_dict.get("updated_at", datetime.now().timestamp())
        
        return workflow


# Global workflow service instance
workflow_service = WorkflowService() 