"""
Comprehensive logging utility for QA Agent application.
Provides structured logging with detailed context for debugging.
"""

import sys
import json
from pathlib import Path
from typing import Any, Dict, Optional
from loguru import logger
from datetime import datetime


class CustomLogger:
    """Custom logger with structured logging and rich context"""

    def __init__(
        self,
        log_file: str = "./logs/app.log",
        log_level: str = "INFO",
        rotation: str = "10 MB",
        retention: str = "30 days",
    ):
        """
        Initialize custom logger

        Args:
            log_file: Path to log file
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            rotation: Log rotation size
            retention: Log retention period
        """
        self.log_file = log_file
        self.log_level = log_level
        self.rotation = rotation
        self.retention = retention

        # Remove default logger
        logger.remove()

        # Add console logger with colors
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
            level=self.log_level,
            colorize=True,
        )

        # Ensure log directory exists
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)

        # Add file logger with rotation
        logger.add(
            self.log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=self.log_level,
            rotation=self.rotation,
            retention=self.retention,
            compression="zip",
        )

        # Add JSON log file for structured logging
        json_log_file = str(Path(self.log_file).with_suffix(".json"))
        logger.add(
            json_log_file,
            format="{message}",
            level=self.log_level,
            rotation=self.rotation,
            retention=self.retention,
            serialize=True,
        )

        self.logger = logger

    def _format_extra(self, extra: Optional[Dict[str, Any]] = None) -> str:
        """Format extra context as JSON string"""
        if extra:
            return f" | Context: {json.dumps(extra, default=str)}"
        return ""

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self.logger.debug(f"{message}{self._format_extra(extra)}")

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self.logger.info(f"{message}{self._format_extra(extra)}")

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self.logger.warning(f"{message}{self._format_extra(extra)}")

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message"""
        self.logger.error(f"{message}{self._format_extra(extra)}")

    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log critical message"""
        self.logger.critical(f"{message}{self._format_extra(extra)}")

    def exception(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log exception with traceback"""
        self.logger.exception(f"{message}{self._format_extra(extra)}")

    def log_function_call(
        self,
        function_name: str,
        args: Optional[Dict[str, Any]] = None,
        status: str = "started",
    ):
        """Log function call with arguments"""
        context = {
            "function": function_name,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if args:
            context["arguments"] = args

        if status == "started":
            self.info(f"Function '{function_name}' started", extra=context)
        elif status == "completed":
            self.info(f"Function '{function_name}' completed successfully", extra=context)
        elif status == "failed":
            self.error(f"Function '{function_name}' failed", extra=context)

    def log_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: Optional[int] = None,
        duration: Optional[float] = None,
    ):
        """Log API request"""
        context = {
            "endpoint": endpoint,
            "method": method,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if status_code:
            context["status_code"] = status_code
        if duration:
            context["duration_ms"] = round(duration * 1000, 2)

        self.info(f"API Request: {method} {endpoint}", extra=context)

    def log_bedrock_request(
        self,
        model_id: str,
        operation: str,
        tokens: Optional[int] = None,
        duration: Optional[float] = None,
    ):
        """Log AWS Bedrock request"""
        context = {
            "model_id": model_id,
            "operation": operation,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if tokens:
            context["tokens"] = tokens
        if duration:
            context["duration_ms"] = round(duration * 1000, 2)

        self.info(f"Bedrock Request: {operation} using {model_id}", extra=context)

    def log_document_processing(
        self,
        filename: str,
        file_type: str,
        status: str,
        chunks: Optional[int] = None,
        error: Optional[str] = None,
    ):
        """Log document processing"""
        context = {
            "filename": filename,
            "file_type": file_type,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if chunks:
            context["chunks"] = chunks
        if error:
            context["error"] = error

        if status == "success":
            self.info(f"Document processed: {filename}", extra=context)
        else:
            self.error(f"Document processing failed: {filename}", extra=context)

    def log_vector_db_operation(
        self,
        operation: str,
        collection: str,
        documents: Optional[int] = None,
        status: str = "success",
    ):
        """Log vector database operation"""
        context = {
            "operation": operation,
            "collection": collection,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if documents:
            context["documents"] = documents

        self.info(f"Vector DB {operation}: {collection}", extra=context)

    def log_test_generation(
        self,
        test_type: str,
        test_count: Optional[int] = None,
        duration: Optional[float] = None,
        status: str = "success",
    ):
        """Log test generation"""
        context = {
            "test_type": test_type,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if test_count:
            context["test_count"] = test_count
        if duration:
            context["duration_ms"] = round(duration * 1000, 2)

        self.info(f"Test Generation: {test_type}", extra=context)


# Create global logger instance
def get_logger() -> CustomLogger:
    """Get global logger instance"""
    from backend.config import settings

    return CustomLogger(
        log_file=settings.log_file_path,
        log_level=settings.log_level,
        rotation=settings.log_rotation,
        retention=settings.log_retention,
    )


# Global logger instance
app_logger = None


def init_logger():
    """Initialize global logger"""
    global app_logger
    if app_logger is None:
        app_logger = get_logger()
        app_logger.info("Logger initialized successfully")
    return app_logger
