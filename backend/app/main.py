"""
FastAPI application for QA Agent - Test Case and Script Generator
"""

import os
from datetime import datetime
from typing import List
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.app.utils.logger import init_logger
from backend.app.models import (
    BuildKnowledgeBaseRequest,
    BuildKnowledgeBaseResponse,
    GenerateTestCasesRequest,
    TestCaseResponse,
    GenerateSeleniumScriptRequest,
    SeleniumScriptResponse,
    StatusResponse,
    KnowledgeBaseStatsResponse,
    HealthCheckResponse,
)
from backend.app.services.vector_store import get_vector_store
from backend.app.services.test_case_generator import get_test_case_generator
from backend.app.services.selenium_generator import get_selenium_generator
from backend.app.services.bedrock_client import get_bedrock_client

# Initialize logger
logger = init_logger()

# Create FastAPI app
app = FastAPI(
    title="QA Agent API",
    description="Autonomous QA Agent for Test Case and Selenium Script Generation",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary storage for uploaded files
UPLOAD_DIR = Path("./uploaded_files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting QA Agent API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"AWS Region: {settings.aws_region}")

    try:
        # Initialize services
        bedrock_client = get_bedrock_client()
        vector_store = get_vector_store()

        logger.info("All services initialized successfully")

    except Exception as e:
        logger.exception("Error initializing services")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down QA Agent API")


@app.get("/", response_model=StatusResponse)
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")

    return StatusResponse(
        success=True,
        message=f"QA Agent API v{settings.app_version} is running"
    )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")

    try:
        # Check Bedrock connection
        bedrock_client = get_bedrock_client()
        bedrock_status = "healthy"

        # Check vector store
        vector_store = get_vector_store()
        vector_stats = vector_store.get_stats()
        vector_status = "healthy"

        return HealthCheckResponse(
            status="healthy",
            app_name=settings.app_name,
            version=settings.app_version,
            timestamp=datetime.utcnow().isoformat(),
            services={
                "bedrock": bedrock_status,
                "vector_store": vector_status,
                "documents_indexed": str(vector_stats['num_documents'])
            }
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheckResponse(
            status="unhealthy",
            app_name=settings.app_name,
            version=settings.app_version,
            timestamp=datetime.utcnow().isoformat(),
            services={
                "error": str(e)
            }
        )


@app.post("/api/upload-documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload support documents for knowledge base
    """
    logger.info(f"Uploading {len(files)} documents")

    try:
        uploaded_files = []

        for file in files:
            # Check file extension
            file_ext = Path(file.filename).suffix.lower()

            if file_ext not in settings.allowed_extensions:
                logger.warning(f"Unsupported file type: {file.filename}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type: {file_ext}. Allowed: {settings.allowed_extensions}"
                )

            # Save file
            file_path = UPLOAD_DIR / file.filename

            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            uploaded_files.append(str(file_path))

            logger.info(f"Saved file: {file.filename} ({len(content)} bytes)")

        logger.info(f"Successfully uploaded {len(uploaded_files)} files")

        return {
            "success": True,
            "message": f"Uploaded {len(uploaded_files)} files successfully",
            "files": [Path(f).name for f in uploaded_files],
            "file_paths": uploaded_files
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error uploading documents")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading documents: {str(e)}"
        )


@app.post("/api/build-knowledge-base", response_model=BuildKnowledgeBaseResponse)
async def build_knowledge_base(
    request: BuildKnowledgeBaseRequest
):
    """
    Build knowledge base from uploaded documents
    """
    logger.info("Building knowledge base")
    logger.log_api_request("/api/build-knowledge-base", "POST")

    try:
        # Get file paths from request or upload directory
        file_paths = request.file_paths
        if file_paths is None:
            file_paths = [str(f) for f in UPLOAD_DIR.glob("*") if f.is_file()]

        if not file_paths:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files found. Please upload documents first."
            )

        logger.info(f"Building knowledge base from {len(file_paths)} files")

        # Build knowledge base
        vector_store = get_vector_store()
        result = vector_store.build_knowledge_base(
            file_paths=file_paths,
            clear_existing=request.clear_existing
        )

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result['message']
            )

        logger.info("Knowledge base built successfully")

        return BuildKnowledgeBaseResponse(
            success=True,
            message=result['message'],
            files_processed=result['files_processed'],
            chunks_created=result['chunks_created'],
            documents_added=result['documents_added'],
            collection_name=result['collection_name'],
            num_documents=result['num_documents']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error building knowledge base")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error building knowledge base: {str(e)}"
        )


@app.get("/api/knowledge-base/stats", response_model=KnowledgeBaseStatsResponse)
async def get_knowledge_base_stats():
    """Get knowledge base statistics"""
    logger.info("Getting knowledge base stats")

    try:
        vector_store = get_vector_store()
        stats = vector_store.get_stats()

        return KnowledgeBaseStatsResponse(
            success=True,
            message="Knowledge base statistics retrieved",
            stats=stats
        )

    except Exception as e:
        logger.exception("Error getting knowledge base stats")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@app.post("/api/generate-test-cases", response_model=TestCaseResponse)
async def generate_test_cases(request: GenerateTestCasesRequest):
    """
    Generate test cases based on query
    """
    logger.info(f"Generating test cases for query: {request.query}")
    logger.log_api_request("/api/generate-test-cases", "POST")

    try:
        # Generate test cases
        generator = get_test_case_generator()

        result = generator.generate_test_cases(
            query=request.query,
            top_k=request.top_k,
            include_positive=request.include_positive,
            include_negative=request.include_negative,
            include_edge_cases=request.include_edge_cases
        )

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['message']
            )

        logger.info(f"Generated {len(result['test_cases'])} test cases")

        return TestCaseResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error generating test cases")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating test cases: {str(e)}"
        )


@app.post("/api/generate-all-test-cases", response_model=TestCaseResponse)
async def generate_all_test_cases():
    """
    Generate comprehensive test cases for all features
    """
    logger.info("Generating all test cases")
    logger.log_api_request("/api/generate-all-test-cases", "POST")

    try:
        generator = get_test_case_generator()
        result = generator.generate_all_test_cases()

        logger.info(f"Generated {len(result['test_cases'])} total test cases")

        return TestCaseResponse(**result)

    except Exception as e:
        logger.exception("Error generating all test cases")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@app.post("/api/generate-selenium-script", response_model=SeleniumScriptResponse)
async def generate_selenium_script(request: GenerateSeleniumScriptRequest):
    """
    Generate Selenium Python script from test case
    """
    test_id = request.test_case.get('test_id', 'Unknown')
    logger.info(f"Generating Selenium script for test: {test_id}")
    logger.log_api_request("/api/generate-selenium-script", "POST")

    try:
        generator = get_selenium_generator()

        if request.save_to_file:
            result = generator.generate_and_save_script(
                test_case=request.test_case,
                html_content=request.html_content
            )
        else:
            result = generator.generate_selenium_script(
                test_case=request.test_case,
                html_content=request.html_content,
                top_k=request.top_k
            )

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['message']
            )

        logger.info(f"Selenium script generated for test: {test_id}")

        return SeleniumScriptResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error generating Selenium script")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@app.delete("/api/clear-knowledge-base", response_model=StatusResponse)
async def clear_knowledge_base():
    """Clear knowledge base"""
    logger.warning("Clearing knowledge base")

    try:
        vector_store = get_vector_store()
        vector_store.clear()

        logger.info("Knowledge base cleared successfully")

        return StatusResponse(
            success=True,
            message="Knowledge base cleared successfully"
        )

    except Exception as e:
        logger.exception("Error clearing knowledge base")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.exception(f"Unhandled exception: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting QA Agent API on {settings.api_host}:{settings.api_port}")

    uvicorn.run(
        "backend.app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
