"""
Configuration management for PocketFlow.

This module handles loading and managing configuration from multiple sources.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from .models import ConfigModel


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # Email Configuration
    EMAIL_HOST: str = Field(env="EMAIL_HOST")
    EMAIL_PORT: int = Field(default=587, env="EMAIL_PORT")
    EMAIL_USERNAME: str = Field(env="EMAIL_USERNAME")
    EMAIL_PASSWORD: str = Field(env="EMAIL_PASSWORD")
    EMAIL_USE_TLS: bool = Field(default=True, env="EMAIL_USE_TLS")
    
    # LLM Configuration
    LLM_PROVIDER: str = Field(default="openai", env="LLM_PROVIDER")
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    GOOGLE_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    LLM_MODEL: str = Field(default="gpt-4", env="LLM_MODEL")
    LLM_MAX_TOKENS: int = Field(default=4000, env="LLM_MAX_TOKENS")
    LLM_TEMPERATURE: float = Field(default=0.7, env="LLM_TEMPERATURE")
    
    # Content Generation
    CONTENT_OUTPUT_DIR: str = Field(default="./generated", env="CONTENT_OUTPUT_DIR")
    MAX_CONTENT_DURATION: int = Field(default=300, env="MAX_CONTENT_DURATION")  # 5 minutes
    
    # Bitcoin Configuration
    ELECTRUM_HOST: str = Field(default="localhost", env="ELECTRUM_HOST")
    ELECTRUM_PORT: int = Field(default=50001, env="ELECTRUM_PORT")
    ELECTRUM_USERNAME: Optional[str] = Field(default=None, env="ELECTRUM_USERNAME")
    ELECTRUM_PASSWORD: Optional[str] = Field(default=None, env="ELECTRUM_PASSWORD")
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///pocketflow.db", env="DATABASE_URL")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Flow Configuration
    FLOW_TIMEOUT: int = Field(default=300, env="FLOW_TIMEOUT")  # 5 minutes
    MAX_RETRIES: int = Field(default=3, env="MAX_RETRIES")
    
    # Security
    GREENLIST_FILE: str = Field(default="greenlist.yaml", env="GREENLIST_FILE")
    TOKEN_PRICE_USD: float = Field(default=0.01, env="TOKEN_PRICE_USD")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields from environment


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path("config")
        self.settings = Settings()
        self._config_cache: Dict[str, Any] = {}
    
    def load_config(self, name: str) -> ConfigModel:
        """Load configuration from YAML file."""
        if name in self._config_cache:
            return self._config_cache[name]
        
        config_file = self.config_dir / f"{name}.yaml"
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        config = ConfigModel(**config_data)
        self._config_cache[name] = config
        return config
    
    def get_environment_config(self) -> ConfigModel:
        """Get configuration for current environment."""
        env = self.settings.ENVIRONMENT
        return self.load_config(env)
    
    def reload_config(self, name: str) -> ConfigModel:
        """Reload configuration from file."""
        if name in self._config_cache:
            del self._config_cache[name]
        return self.load_config(name)
    
    def validate_config(self, config: ConfigModel) -> bool:
        """Validate configuration."""
        try:
            # Add validation logic here
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False


# Global configuration manager instance
config_manager = ConfigManager()


def get_settings() -> Settings:
    """Get application settings."""
    return config_manager.settings


def get_config(name: str = None) -> ConfigModel:
    """Get configuration by name or current environment."""
    if name is None:
        return config_manager.get_environment_config()
    return config_manager.load_config(name) 