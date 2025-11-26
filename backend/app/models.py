"""
Pydantic models for API request/response validation
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# Request Models
class BuildKnowledgeBaseRequest(BaseModel):
    """Request model for building knowledge base"""
    clear_existing: bool = Field(
        default=True,
        description="Whether to clear existing knowledge base"
    )
    file_paths: Optional[List[str]] = Field(
        default=None,
        description="Optional list of file paths to process"
    )


class GenerateTestCasesRequest(BaseModel):
    """Request model for generating test cases"""
    query: str = Field(
        ...,
        description="Query describing what test cases to generate",
        min_length=3
    )
    top_k: int = Field(
        default=5,
        description="Number of relevant documents to retrieve",
        ge=1,
        le=20
    )
    include_positive: bool = Field(
        default=True,
        description="Include positive test scenarios"
    )
    include_negative: bool = Field(
        default=True,
        description="Include negative test scenarios"
    )
    include_edge_cases: bool = Field(
        default=True,
        description="Include edge case scenarios"
    )


class GenerateSeleniumScriptRequest(BaseModel):
    """Request model for generating Selenium script"""
    test_case: Dict[str, Any] = Field(
        ...,
        description="Test case dictionary"
    )
    html_content: Optional[str] = Field(
        default=None,
        description="HTML content of the page to test"
    )
    top_k: int = Field(
        default=5,
        description="Number of relevant documents to retrieve",
        ge=1,
        le=20
    )
    save_to_file: bool = Field(
        default=False,
        description="Whether to save script to file"
    )


# Response Models
class StatusResponse(BaseModel):
    """Generic status response"""
    success: bool
    message: str


class KnowledgeBaseStatsResponse(BaseModel):
    """Knowledge base statistics response"""
    success: bool
    message: str
    stats: Dict[str, Any]


class BuildKnowledgeBaseResponse(BaseModel):
    """Build knowledge base response"""
    success: bool
    message: str
    files_processed: int
    chunks_created: int
    documents_added: int
    collection_name: str
    num_documents: int


class TestCaseResponse(BaseModel):
    """Test case response"""
    success: bool
    message: str
    test_cases: List[Dict[str, Any]]
    sources: Optional[List[str]] = None
    query: Optional[str] = None
    generation_time: Optional[float] = None


class SeleniumScriptResponse(BaseModel):
    """Selenium script response"""
    success: bool
    message: str
    script: Optional[str] = None
    test_id: Optional[str] = None
    feature: Optional[str] = None
    file_path: Optional[str] = None
    generation_time: Optional[float] = None
    sources: Optional[List[str]] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    app_name: str
    version: str
    timestamp: str
    services: Dict[str, str]
