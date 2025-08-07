"""
File operation tools for PocketFlow agents.
"""

import os
from pathlib import Path
from typing import Dict, Any
from .base import Tool, ToolResult
from ..utils.logging import get_logger


class FileReadTool(Tool):
    """
    Tool for reading files safely.
    """
    
    def __init__(self):
        super().__init__(
            name="file_read",
            description="Read the contents of a file"
        )
    
    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "file_path": {
                "type": str,
                "required": True,
                "description": "Path to the file to read"
            },
            "max_size": {
                "type": int,
                "required": False,
                "description": "Maximum file size to read in bytes (default: 1MB)"
            }
        }
    
    def execute(self, **kwargs) -> ToolResult:
        """
        Read a file safely.
        
        Args:
            file_path: Path to the file
            max_size: Maximum file size to read
            
        Returns:
            ToolResult with file contents
        """
        file_path = kwargs.get("file_path")
        max_size = kwargs.get("max_size", 1024 * 1024)  # 1MB default
        
        try:
            # Validate file path
            if not self._is_safe_path(file_path):
                return ToolResult(
                    success=False,
                    error="Invalid file path"
                )
            
            # Check if file exists
            if not os.path.exists(file_path):
                return ToolResult(
                    success=False,
                    error="File does not exist"
                )
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > max_size:
                return ToolResult(
                    success=False,
                    error=f"File too large ({file_size} bytes, max {max_size})"
                )
            
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return ToolResult(
                success=True,
                data={
                    "file_path": file_path,
                    "content": content,
                    "size": file_size
                },
                metadata={
                    "source": "file_read"
                }
            )
            
        except Exception as e:
            self.logger.error(f"File read failed: {str(e)}")
            return ToolResult(
                success=False,
                error=f"File read failed: {str(e)}"
            )
    
    def _is_safe_path(self, file_path: str) -> bool:
        """
        Check if the file path is safe to access.
        
        Args:
            file_path: The file path to check
            
        Returns:
            True if safe, False otherwise
        """
        # Prevent directory traversal
        if ".." in file_path:
            return False
        
        # Only allow files in specific directories
        safe_dirs = ["/opt/pocketflow/data", "/tmp"]
        file_path = os.path.abspath(file_path)
        
        return any(file_path.startswith(safe_dir) for safe_dir in safe_dirs)


class FileWriteTool(Tool):
    """
    Tool for writing files safely.
    """
    
    def __init__(self):
        super().__init__(
            name="file_write",
            description="Write content to a file"
        )
    
    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "file_path": {
                "type": str,
                "required": True,
                "description": "Path to the file to write"
            },
            "content": {
                "type": str,
                "required": True,
                "description": "Content to write to the file"
            },
            "mode": {
                "type": str,
                "required": False,
                "description": "Write mode: 'w' (overwrite) or 'a' (append) (default: 'w')"
            }
        }
    
    def execute(self, **kwargs) -> ToolResult:
        """
        Write content to a file safely.
        
        Args:
            file_path: Path to the file
            content: Content to write
            mode: Write mode ('w' or 'a')
            
        Returns:
            ToolResult with write status
        """
        file_path = kwargs.get("file_path")
        content = kwargs.get("content")
        mode = kwargs.get("mode", "w")
        
        try:
            # Validate file path
            if not self._is_safe_path(file_path):
                return ToolResult(
                    success=False,
                    error="Invalid file path"
                )
            
            # Validate mode
            if mode not in ["w", "a"]:
                return ToolResult(
                    success=False,
                    error="Invalid write mode"
                )
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write file
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            return ToolResult(
                success=True,
                data={
                    "file_path": file_path,
                    "bytes_written": len(content),
                    "mode": mode
                },
                metadata={
                    "source": "file_write"
                }
            )
            
        except Exception as e:
            self.logger.error(f"File write failed: {str(e)}")
            return ToolResult(
                success=False,
                error=f"File write failed: {str(e)}"
            )
    
    def _is_safe_path(self, file_path: str) -> bool:
        """
        Check if the file path is safe to write to.
        
        Args:
            file_path: The file path to check
            
        Returns:
            True if safe, False otherwise
        """
        # Prevent directory traversal
        if ".." in file_path:
            return False
        
        # Only allow writing to specific directories
        safe_dirs = ["/opt/pocketflow/data", "/tmp"]
        file_path = os.path.abspath(file_path)
        
        return any(file_path.startswith(safe_dir) for safe_dir in safe_dirs) 