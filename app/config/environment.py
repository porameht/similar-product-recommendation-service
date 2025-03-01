"""Environment configuration utilities.

This module provides utilities for loading and managing environment-specific
configuration.
"""

import os
from enum import Enum
from typing import Optional


class Environment(str, Enum):
    """Environment enum for application configuration."""
    
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    

def get_environment() -> Environment:
    """Get the current environment.
    
    Returns:
        Environment: Current environment (development, testing, or production)
    """
    env_str = os.getenv("APP_ENV", "development").lower()
    
    if env_str == "production":
        return Environment.PRODUCTION
    elif env_str == "testing":
        return Environment.TESTING
    else:
        return Environment.DEVELOPMENT


def load_env_file(env: Optional[Environment] = None) -> None:
    """Load environment-specific .env file.
    
    Args:
        env: Environment to load, if None uses current environment
    """
    from dotenv import load_dotenv
    
    if env is None:
        env = get_environment()
    
    load_dotenv(dotenv_path=".env", override=False)
    
    env_file = f".env.{env.value}"
    if os.path.exists(env_file):
        load_dotenv(dotenv_path=env_file, override=True) 