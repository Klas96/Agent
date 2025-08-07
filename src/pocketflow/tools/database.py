"""
Database query tool for PocketFlow agents.
"""

import sqlite3
from typing import Dict, Any, List
from .base import Tool, ToolResult
from ..utils.logging import get_logger


class DatabaseQueryTool(Tool):
    """
    Tool for querying the PocketFlow database safely.
    """
    
    def __init__(self):
        super().__init__(
            name="database_query",
            description="Query the PocketFlow database for user and system information"
        )
    
    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "query": {
                "type": str,
                "required": True,
                "description": "SQL query to execute (SELECT only)"
            },
            "max_rows": {
                "type": int,
                "required": False,
                "description": "Maximum number of rows to return (default: 100)"
            }
        }
    
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute a database query safely.
        
        Args:
            query: The SQL query to execute
            max_rows: Maximum number of rows to return
            
        Returns:
            ToolResult with query results
        """
        query = kwargs.get("query")
        max_rows = kwargs.get("max_rows", 100)
        
        try:
            # Validate query
            if not self._is_safe_query(query):
                return ToolResult(
                    success=False,
                    error="Invalid or unsafe query"
                )
            
            # Execute query
            results = self._execute_query(query, max_rows)
            
            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "results": results,
                    "row_count": len(results)
                },
                metadata={
                    "source": "database_query"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Database query failed: {str(e)}")
            return ToolResult(
                success=False,
                error=f"Database query failed: {str(e)}"
            )
    
    def _is_safe_query(self, query: str) -> bool:
        """
        Check if the query is safe to execute.
        
        Args:
            query: The SQL query to check
            
        Returns:
            True if safe, False otherwise
        """
        # Only allow SELECT queries
        query_upper = query.strip().upper()
        if not query_upper.startswith("SELECT"):
            return False
        
        # Prevent common SQL injection patterns
        dangerous_patterns = [
            "DROP", "DELETE", "UPDATE", "INSERT", "CREATE", "ALTER",
            "EXEC", "EXECUTE", "UNION", "INTO", "OUTFILE", "DUMPFILE"
        ]
        
        for pattern in dangerous_patterns:
            if pattern in query_upper:
                return False
        
        return True
    
    def _execute_query(self, query: str, max_rows: int) -> List[Dict[str, Any]]:
        """
        Execute a safe SQL query.
        
        Args:
            query: The SQL query
            max_rows: Maximum rows to return
            
        Returns:
            List of result dictionaries
        """
        db_path = "/opt/pocketflow/data/pocketflow.db"
        
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Add LIMIT clause if not present
            if "LIMIT" not in query.upper():
                query += f" LIMIT {max_rows}"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            results = []
            for row in rows:
                results.append(dict(row))
            
            return results 