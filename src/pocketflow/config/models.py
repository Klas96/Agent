"""
Configuration models for PocketFlow.

This module defines the data models used for configuration.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class EmailConfig(BaseModel):
    """Email service configuration."""
    host: str = Field(description="SMTP host")
    port: int = Field(default=587, description="SMTP port")
    username: str = Field(description="Email username")
    password: str = Field(description="Email password")
    use_tls: bool = Field(default=True, description="Use TLS")
    from_address: str = Field(description="From email address")
    max_emails_per_batch: int = Field(default=10, description="Max emails to process per batch")


class LLMConfig(BaseModel):
    """LLM service configuration."""
    provider: str = Field(default="openai", description="LLM provider")
    model: str = Field(default="gpt-4", description="Model name")
    api_key: Optional[str] = Field(default=None, description="API key")
    ollama_host: str = Field(default="localhost", description="Ollama host")
    ollama_port: int = Field(default=11434, description="Ollama port")
    ollama_model: str = Field(default="llama3:latest", description="Ollama model")
    max_tokens: int = Field(default=4000, description="Maximum tokens")
    temperature: float = Field(default=0.7, description="Temperature")
    timeout: int = Field(default=60, description="Request timeout in seconds")


class ContentConfig(BaseModel):
    """Content generation configuration."""
    output_directory: str = Field(default="./generated", description="Output directory")
    max_duration: int = Field(default=300, description="Maximum content duration in seconds")
    supported_types: List[str] = Field(default=["sound", "image", "document"], description="Supported content types")
    quality_settings: Dict[str, Any] = Field(default_factory=dict, description="Quality settings per type")


class BitcoinConfig(BaseModel):
    """Bitcoin service configuration."""
    electrum_host: str = Field(default="localhost", description="Electrum host")
    electrum_port: int = Field(default=50001, description="Electrum port")
    username: Optional[str] = Field(default=None, description="Electrum username")
    password: Optional[str] = Field(default=None, description="Electrum password")
    network: str = Field(default="mainnet", description="Bitcoin network")
    token_price_usd: float = Field(default=0.01, description="Token price in USD")


class DatabaseConfig(BaseModel):
    """Database configuration."""
    url: str = Field(description="Database URL")
    pool_size: int = Field(default=10, description="Connection pool size")
    max_overflow: int = Field(default=20, description="Max overflow connections")
    echo: bool = Field(default=False, description="Echo SQL queries")


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO", description="Log level")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format")
    file: Optional[str] = Field(default=None, description="Log file path")
    max_size: int = Field(default=10, description="Max log file size in MB")
    backup_count: int = Field(default=5, description="Number of backup files")


class FlowConfig(BaseModel):
    """Flow configuration."""
    timeout: int = Field(default=300, description="Flow timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retries per node")
    enable_monitoring: bool = Field(default=True, description="Enable flow monitoring")
    parallel_execution: bool = Field(default=False, description="Enable parallel node execution")


class SecurityConfig(BaseModel):
    """Security configuration."""
    allowed_domains: List[str] = Field(default_factory=list, description="Allowed email domains")
    allowed_emails: List[str] = Field(default_factory=list, description="Allowed email addresses")
    require_authentication: bool = Field(default=True, description="Require user authentication")


class ConfigModel(BaseModel):
    """Main configuration model."""
    environment: str = Field(default="development", description="Environment name")
    debug: bool = Field(default=False, description="Debug mode")
    
    email: EmailConfig = Field(description="Email configuration")
    llm: LLMConfig = Field(description="LLM configuration")
    content: ContentConfig = Field(description="Content generation configuration")
    bitcoin: BitcoinConfig = Field(description="Bitcoin configuration")
    database: DatabaseConfig = Field(description="Database configuration")
    logging: LoggingConfig = Field(description="Logging configuration")
    flow: FlowConfig = Field(description="Flow configuration")
    security: SecurityConfig = Field(description="Security configuration")
    
    # Optional custom configurations
    custom: Dict[str, Any] = Field(default_factory=dict, description="Custom configuration")
    
    class Config:
        extra = "forbid"
        validate_assignment = True 