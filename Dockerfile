# Multi-stage Dockerfile for QA Agent

# Base stage
FROM python:3.10-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Backend stage
FROM base as backend

WORKDIR /app

# Copy backend code
COPY backend/ ./backend/
COPY .env.example .env

# Create necessary directories
RUN mkdir -p logs vector_store generated_tests/selenium_scripts uploaded_files

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend stage
FROM base as frontend

WORKDIR /app

# Copy frontend code
COPY frontend/ ./frontend/
COPY .env.example .env

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
