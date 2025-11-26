"""
Configuration management for QA Agent application.
Loads settings from environment variables with validation.
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # AWS Bedrock Configuration
    aws_access_key_id: Optional[str] = Field(
        default=None,
        description="AWS Access Key ID (optional when using IAM roles)"
    )
    aws_secret_access_key: Optional[str] = Field(
        default=None,
        description="AWS Secret Access Key (optional when using IAM roles)"
    )
    aws_region: str = Field(default="us-east-1", description="AWS Region")

    # AWS Bedrock Model IDs
    bedrock_llm_model_id: str = Field(
        default="amazon.nova-lite-v1:0",
        description="Bedrock LLM Model ID"
    )
    bedrock_embedding_model_id: str = Field(
        default="cohere.embed-v4:0",
        description="Bedrock Embedding Model ID"
    )

    # Application Configuration
    app_name: str = Field(default="QA Agent", description="Application Name")
    app_version: str = Field(default="1.0.0", description="Application Version")
    environment: str = Field(default="development", description="Environment")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API Host")
    api_port: int = Field(default=8000, description="API Port")
    api_reload: bool = Field(default=True, description="API Auto-reload")

    # Streamlit Configuration
    streamlit_port: int = Field(default=8501, description="Streamlit Port")

    # Vector Database Configuration
    vector_db_path: str = Field(default="./vector_store", description="Vector DB Path")
    vector_db_collection_name: str = Field(
        default="qa_documents",
        description="Vector DB Collection Name"
    )

    # Chunk Configuration
    chunk_size: int = Field(default=1000, description="Text Chunk Size")
    chunk_overlap: int = Field(default=200, description="Text Chunk Overlap")

    # LLM Configuration
    llm_max_tokens: int = Field(default=4096, description="LLM Max Tokens")
    llm_temperature: float = Field(default=0.7, description="LLM Temperature")
    embedding_dimensions: int = Field(default=1024, description="Embedding Dimensions")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Log Level")
    log_file_path: str = Field(default="./logs/app.log", description="Log File Path")
    log_rotation: str = Field(default="10 MB", description="Log Rotation Size")
    log_retention: str = Field(default="30 days", description="Log Retention Period")

    # File Upload Configuration
    max_upload_size_mb: int = Field(default=50, description="Max Upload Size in MB")
    allowed_extensions: str = Field(
        default=".md,.txt,.json,.pdf,.html,.docx,.doc",
        description="Allowed File Extensions"
    )

    # Generated Files Configuration
    generated_tests_path: str = Field(
        default="./generated_tests",
        description="Generated Tests Path"
    )
    generated_scripts_path: str = Field(
        default="./generated_tests/selenium_scripts",
        description="Generated Scripts Path"
    )

    # Timeout Configuration (seconds)
    bedrock_request_timeout: int = Field(
        default=60,
        description="Bedrock Request Timeout"
    )
    document_processing_timeout: int = Field(
        default=300,
        description="Document Processing Timeout"
    )

    @validator("allowed_extensions")
    def parse_extensions(cls, v):
        """Parse allowed extensions into a list"""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings singleton"""
    return Settings()


def ensure_directories():
    """Ensure all required directories exist"""
    settings = get_settings()

    directories = [
        settings.vector_db_path,
        settings.generated_tests_path,
        settings.generated_scripts_path,
        Path(settings.log_file_path).parent,
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


# Create settings instance
settings = get_settings()

# Ensure directories exist
ensure_directories()
