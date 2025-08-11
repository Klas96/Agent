"""
Job Scheduler Service for PocketFlow.

This service handles the execution of scheduled jobs, similar to n8n's workflow execution.
"""

import json
import time
import threading
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

from ..utils.logging import get_logger
from ..core.flow import FlowBuilder, Flow
from ..core.types import FlowType, SharedState


class JobScheduler:
    """Scheduler for executing scheduled jobs."""
    
    def __init__(self, db_path: str = "/opt/pocketflow/data/pocketflow.db"):
        self.db_path = db_path
        self.logger = get_logger("JobScheduler")
        self.running = False
        self.scheduler_thread = None
        self.active_executions: Dict[int, threading.Thread] = {}
        
    def start(self):
        """Start the job scheduler."""
        if self.running:
            self.logger.warning("Job scheduler is already running")
            return
            
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("Job scheduler started")
        
    def stop(self):
        """Stop the job scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        self.logger.info("Job scheduler stopped")
        
    def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.running:
            try:
                self._check_and_run_jobs()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)
                
    def _check_and_run_jobs(self):
        """Check for jobs that need to be executed."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get active jobs that are due to run
            cursor.execute("""
                SELECT id, name, job_type, flow_config, schedule
                FROM scheduled_jobs 
                WHERE is_active = 1
            """)
            
            jobs = cursor.fetchall()
            conn.close()
            
            for job_id, name, job_type, flow_config, schedule in jobs:
                if self._should_run_job(schedule):
                    self.logger.info(f"Job {name} (ID: {job_id}) is due to run")
                    self._execute_job(job_id, name, job_type, flow_config)
                    
        except Exception as e:
            self.logger.error(f"Error checking jobs: {e}")
            
    def _should_run_job(self, schedule: str) -> bool:
        """Check if a job should run based on its schedule."""
        try:
            # Simple cron-like schedule checking
            # Format: minute hour day month weekday
            parts = schedule.split()
            if len(parts) != 5:
                return False
                
            now = datetime.now()
            minute, hour, day, month, weekday = parts
            
            # Check if current time matches schedule
            if not self._matches_cron_field(minute, now.minute):
                return False
            if not self._matches_cron_field(hour, now.hour):
                return False
            if not self._matches_cron_field(day, now.day):
                return False
            if not self._matches_cron_field(month, now.month):
                return False
            if not self._matches_cron_field(weekday, now.weekday()):
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking schedule {schedule}: {e}")
            return False
            
    def _matches_cron_field(self, field: str, value: int) -> bool:
        """Check if a value matches a cron field."""
        if field == "*":
            return True
        if field.isdigit():
            return int(field) == value
        if "/" in field:
            step_part, step = field.split("/")
            if step_part == "*":
                return value % int(step) == 0
        if "," in field:
            return value in [int(x) for x in field.split(",")]
        if "-" in field:
            start, end = field.split("-")
            return int(start) <= value <= int(end)
        return False
        
    def _execute_job(self, job_id: int, name: str, job_type: str, flow_config: str):
        """Execute a scheduled job."""
        try:
            # Create execution record
            execution_id = self._create_execution_record(job_id)
            
            # Start execution in separate thread
            execution_thread = threading.Thread(
                target=self._run_job_execution,
                args=(execution_id, job_id, name, job_type, flow_config),
                daemon=True
            )
            execution_thread.start()
            
            # Track active execution
            self.active_executions[execution_id] = execution_thread
            
            self.logger.info(f"Started execution {execution_id} for job {name}")
            
        except Exception as e:
            self.logger.error(f"Error starting job execution for {name}: {e}")
            
    def _create_execution_record(self, job_id: int) -> int:
        """Create a new execution record in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO job_executions (job_id, status, started_at)
            VALUES (?, 'running', CURRENT_TIMESTAMP)
        """, (job_id,))
        
        execution_id = cursor.lastrowid
        
        # Update job's last_run
        cursor.execute("""
            UPDATE scheduled_jobs 
            SET last_run = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (job_id,))
        
        conn.commit()
        conn.close()
        
        return execution_id
        
    def _run_job_execution(self, execution_id: int, job_id: int, name: str, job_type: str, flow_config: str):
        """Run a job execution."""
        try:
            self.logger.info(f"Running job execution {execution_id} for {name}")
            
            # Parse flow configuration
            config = json.loads(flow_config)
            
            # Create shared state
            shared = SharedState()
            shared.job_id = job_id
            shared.job_name = name
            shared.job_type = job_type
            shared.execution_id = execution_id
            
            # Execute the flow based on job type
            result = self._execute_flow_by_type(job_type, config, shared)
            
            # Update execution record
            self._update_execution_record(execution_id, "completed", result)
            
            self.logger.info(f"Completed job execution {execution_id} for {name}")
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Job execution {execution_id} failed: {error_msg}")
            self._update_execution_record(execution_id, "failed", None, error_msg)
            
        finally:
            # Remove from active executions
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
                
    def _execute_flow_by_type(self, job_type: str, config: Dict[str, Any], shared: SharedState) -> Dict[str, Any]:
        """Execute a flow based on job type."""
        try:
            if job_type == "email_processor":
                return self._execute_email_processor(config, shared)
            elif job_type == "content_generation":
                return self._execute_content_generation(config, shared)
            elif job_type == "data_backup":
                return self._execute_data_backup(config, shared)
            elif job_type == "system_maintenance":
                return self._execute_system_maintenance(config, shared)
            elif job_type == "custom_flow":
                return self._execute_custom_flow(config, shared)
            else:
                raise ValueError(f"Unknown job type: {job_type}")
                
        except Exception as e:
            self.logger.error(f"Error executing flow for job type {job_type}: {e}")
            raise
            
    def _execute_email_processor(self, config: Dict[str, Any], shared: SharedState) -> Dict[str, Any]:
        """Execute email processor flow."""
        # Import here to avoid circular imports
        from ..flows.email_processor import EmailProcessorFlow
        
        flow = EmailProcessorFlow()
        result = flow.run(shared)
        
        return {
            "flow_type": "email_processor",
            "result": result,
            "processed_emails": getattr(shared, 'processed_count', 0)
        }
        
    def _execute_content_generation(self, config: Dict[str, Any], shared: SharedState) -> Dict[str, Any]:
        """Execute content generation flow."""
        # Import here to avoid circular imports
        from ..flows.content_generation import ContentGenerationFlow
        
        flow = ContentGenerationFlow()
        result = flow.run(shared)
        
        return {
            "flow_type": "content_generation",
            "result": result,
            "generated_content": getattr(shared, 'generated_files', [])
        }
        
    def _execute_data_backup(self, config: Dict[str, Any], shared: SharedState) -> Dict[str, Any]:
        """Execute data backup flow."""
        # Simple backup implementation
        backup_path = f"/opt/pocketflow/backups/backup_{int(time.time())}.db"
        Path(backup_path).parent.mkdir(exist_ok=True)
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        
        return {
            "flow_type": "data_backup",
            "backup_path": backup_path,
            "backup_size": Path(backup_path).stat().st_size
        }
        
    def _execute_system_maintenance(self, config: Dict[str, Any], shared: SharedState) -> Dict[str, Any]:
        """Execute system maintenance flow."""
        # Simple maintenance tasks
        maintenance_results = []
        
        # Clean old log files
        log_dir = Path("/opt/pocketflow/logs")
        if log_dir.exists():
            for log_file in log_dir.glob("*.log.*"):
                if log_file.stat().st_mtime < time.time() - 7 * 24 * 3600:  # 7 days old
                    log_file.unlink()
                    maintenance_results.append(f"Deleted old log: {log_file.name}")
                    
        # Clean old job executions
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM job_executions 
            WHERE started_at < datetime('now', '-30 days')
        """)
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        maintenance_results.append(f"Cleaned {deleted_count} old job executions")
        
        return {
            "flow_type": "system_maintenance",
            "maintenance_tasks": maintenance_results
        }
        
    def _execute_custom_flow(self, config: Dict[str, Any], shared: SharedState) -> Dict[str, Any]:
        """Execute custom flow based on configuration."""
        # This would be a more sophisticated flow execution system
        # For now, just return the config
        return {
            "flow_type": "custom_flow",
            "config": config,
            "message": "Custom flow execution not yet implemented"
        }
        
    def _update_execution_record(self, execution_id: int, status: str, result: Optional[str] = None, error_message: Optional[str] = None):
        """Update an execution record in the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if result:
                result_json = json.dumps(result)
            else:
                result_json = None
                
            cursor.execute("""
                UPDATE job_executions 
                SET status = ?, completed_at = CURRENT_TIMESTAMP, result = ?, error_message = ?
                WHERE id = ?
            """, (status, result_json, error_message, execution_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error updating execution record {execution_id}: {e}")
            
    def run_job_now(self, job_id: int) -> bool:
        """Run a job immediately."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name, job_type, flow_config
                FROM scheduled_jobs 
                WHERE id = ?
            """, (job_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                self.logger.error(f"Job {job_id} not found")
                return False
                
            name, job_type, flow_config = result
            self._execute_job(job_id, name, job_type, flow_config)
            return True
            
        except Exception as e:
            self.logger.error(f"Error running job {job_id} now: {e}")
            return False
            
    def get_active_executions(self) -> List[Dict[str, Any]]:
        """Get list of active executions."""
        return [
            {
                "execution_id": exec_id,
                "thread_alive": thread.is_alive()
            }
            for exec_id, thread in self.active_executions.items()
        ]
        
    def stop_execution(self, execution_id: int) -> bool:
        """Stop a running execution."""
        if execution_id in self.active_executions:
            # Mark as stopped in database
            self._update_execution_record(execution_id, "stopped")
            del self.active_executions[execution_id]
            return True
        return False


# Global scheduler instance
_scheduler_instance: Optional[JobScheduler] = None

def get_scheduler() -> JobScheduler:
    """Get the global scheduler instance."""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = JobScheduler()
    return _scheduler_instance

def start_scheduler():
    """Start the global scheduler."""
    scheduler = get_scheduler()
    scheduler.start()

def stop_scheduler():
    """Stop the global scheduler."""
    global _scheduler_instance
    if _scheduler_instance:
        _scheduler_instance.stop()
        _scheduler_instance = None 