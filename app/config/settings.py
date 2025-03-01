"""Configuration settings for the application.

This module provides a Pydantic Settings class for loading and validating 
application configuration from environment variables.
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    
    # Qdrant settings
    qdrant_host: str = Field(default="localhost", env="QDRANT_HOST") 
    qdrant_port: int = Field(default=6333, env="QDRANT_PORT")
    qdrant_collection: str = Field(default="products", env="QDRANT_COLLECTION")
    
    # Embedding model settings
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    vector_size: int = Field(default=384, env="VECTOR_SIZE")
    
    # Data paths
    data_path: str = Field(default="data/products.csv", env="DATA_PATH")
    snapshots_dir: str = Field(default="snapshots", env="SNAPSHOTS_DIR")
    models_dir: str = Field(default="models", env="MODELS_DIR")
    
    # Recommendation settings
    default_recommendation_limit: int = Field(default=5, env="DEFAULT_RECOMMENDATION_LIMIT")
    distance_threshold: float = Field(default=0.95, env="DISTANCE_THRESHOLD")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings() 