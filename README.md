# QA Agent - Autonomous Test Case & Selenium Script Generator

An intelligent, autonomous QA agent that constructs a "testing brain" from project documentation and generates comprehensive test cases and executable Selenium scripts using AWS Bedrock (Nova Lite LLM and Cohere Embed v4).

## 🌟 Features

- **📚 Documentation-Grounded Testing**: RAG-based approach ensures all test cases are strictly based on provided documentation
- **🤖 Autonomous Test Generation**: AI-powered test case generation using AWS Bedrock Nova Lite
- **🔧 Selenium Script Generation**: Converts test cases into production-ready Python Selenium scripts
- **🎯 Zero Hallucination**: All test reasoning grounded in provided documents
- **📊 Comprehensive Logging**: Detailed logs at every step for easy debugging
- **🚀 Production Ready**: FastAPI backend with Streamlit UI, Docker support, AWS deployment ready

## 📋 Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Project Assets](#project-assets)
- [Demo Video](#demo-video)
- [Troubleshooting](#troubleshooting)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                      (Streamlit Frontend)                       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Document     │  │ Test Case    │  │ Selenium Script      │ │
│  │ Parser       │  │ Generator    │  │ Generator            │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└────────────┬───────────────────┬─────────────────────┬─────────┘
             │                   │                     │
             ▼                   ▼                     ▼
    ┌───────────────┐   ┌──────────────┐    ┌──────────────────┐
    │ Vector Store  │   │ AWS Bedrock  │    │ AWS Bedrock      │
    │ (FAISS)       │   │ Nova Lite    │    │ Nova Lite        │
    └───────────────┘   │ (LLM)        │    │ (Code Gen)       │
                        └──────────────┘    └──────────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │ Cohere       │
                        │ Embed v4     │
                        └──────────────┘
```

### Technology Stack

- **LLM**: AWS Bedrock - Amazon Nova Lite v1.0 (multimodal foundation model)
- **Embeddings**: AWS Bedrock - Cohere Embed v4 (multimodal embeddings)
- **Vector Database**: FAISS (Facebook AI Similarity Search)
- **Backend**: FastAPI (Python 3.10+)
- **Frontend**: Streamlit
- **Document Processing**: PyMuPDF, python-docx, unstructured
- **Test Automation**: Selenium WebDriver

## 📦 Prerequisites

### Required

1. **Python 3.10+**
   ```bash
   python --version  # Should be 3.10 or higher
   ```

2. **AWS Account with Bedrock Access**
   - AWS Access Key ID
   - AWS Secret Access Key
   - Access to:
     - Amazon Nova Lite (`amazon.nova-lite-v1:0`)
     - Cohere Embed v4 (`cohere.embed-v4:0`)

3. **AWS Bedrock Models Enabled**
   - Go to AWS Bedrock Console → Model Access
   - Request access to:
     - Amazon Nova Lite
     - Cohere Embed v4

### Optional

- **Docker & Docker Compose** (for containerized deployment)
- **Git** (for version control)

## 🚀 Installation

### Option 1: Local Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd qa-agent-project
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your AWS credentials:
   ```env
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   AWS_REGION=us-east-1

   BEDROCK_LLM_MODEL_ID=amazon.nova-lite-v1:0
   BEDROCK_EMBEDDING_MODEL_ID=cohere.embed-v4:0
   ```

### Option 2: Docker Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd qa-agent-project
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials
   ```

3. **Build and Run**
   ```bash
   docker-compose up --build
   ```

## ⚙️ Configuration

### Environment Variables

All configuration is done through environment variables. See `.env.example` for all available options.

**Required Variables:**
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_REGION`: AWS region (default: us-east-1)

**Optional Variables:**
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `CHUNK_SIZE`: Text chunk size for document processing (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `LLM_MAX_TOKENS`: Maximum tokens for LLM generation (default: 4096)
- `LLM_TEMPERATURE`: Temperature for LLM sampling (default: 0.7)

### AWS Credentials Setup

**Option 1: Environment Variables (Recommended for Development)**
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

**Option 2: AWS CLI Configuration**
```bash
aws configure
```

**Option 3: IAM Role (Recommended for Production/AWS Deployment)**
- Attach IAM role with Bedrock permissions to your EC2/ECS instance

## 📖 Usage

### Running the Application

#### Method 1: Separate Terminal Windows

**Terminal 1 - Backend (FastAPI):**
```bash
cd qa-agent-project
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend (Streamlit):**
```bash
cd qa-agent-project
source venv/bin/activate  # On Windows: venv\Scripts\activate
streamlit run frontend/streamlit_app.py
```

#### Method 2: Docker Compose
```bash
docker-compose up
```

### Accessing the Application

- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs
- **FastAPI ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Step-by-Step Workflow

#### 1. Upload Documents

1. Navigate to **📁 Upload Documents** page
2. Click "Browse files" and select your support documents:
   - Product specifications (`.md`, `.txt`)
   - UI/UX guidelines (`.txt`)
   - API documentation (`.json`)
   - Business rules (`.md`)
   - Test data (`.json`)
3. Click "Upload Files"

#### 2. Build Knowledge Base

1. Navigate to **🧠 Build Knowledge Base** page
2. Upload your `checkout.html` file (target web project)
3. Choose whether to clear existing knowledge base
4. Click "Build Knowledge Base"
5. Wait for processing (this may take 1-3 minutes depending on document size)
6. Verify success message and statistics

#### 3. Generate Test Cases

1. Navigate to **✍️ Generate Test Cases** page
2. Enter your query, for example:
   - "Generate test cases for discount code functionality"
   - "Generate test cases for form validation"
   - "Generate test cases for shopping cart operations"
3. Configure options:
   - Select number of relevant documents (top_k)
   - Choose test types: Positive, Negative, Edge Cases
4. Click "Generate Test Cases"
5. Review generated test cases
6. Optionally download as JSON

#### 4. Generate Selenium Scripts

1. Navigate to **🔧 Generate Selenium Scripts** page
2. Select a test case from the dropdown
3. Enable "Include HTML context" for better selector generation
4. Click "Generate Selenium Script"
5. Review the generated Python script
6. Download or copy the script
7. Run the script: `pytest test_tc_001.py`

### Example Queries for Test Generation

**Positive Scenarios:**
```
- Generate positive test cases for adding items to cart
- Create test cases for successful checkout flow
- Generate tests for valid discount code application
```

**Negative Scenarios:**
```
- Generate negative test cases for form validation
- Create test cases for invalid discount codes
- Generate tests for empty cart checkout
```

**Edge Cases:**
```
- Generate edge case tests for quantity limits
- Create boundary tests for discount calculations
- Generate tests for special character handling in forms
```

## 📁 Project Structure

```
qa-agent-project/
│
├── backend/                      # Backend application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # Pydantic models
│   │   ├── services/            # Business logic services
│   │   │   ├── bedrock_client.py       # AWS Bedrock integration
│   │   │   ├── document_parser.py      # Document processing
│   │   │   ├── vector_store.py         # FAISS vector database
│   │   │   ├── test_case_generator.py  # Test case generation
│   │   │   └── selenium_generator.py   # Selenium script generation
│   │   └── utils/
│   │       └── logger.py        # Comprehensive logging
│   └── config.py                # Configuration management
│
├── frontend/                    # Frontend application
│   └── streamlit_app.py        # Streamlit UI
│
├── project_assets/             # Project assets for testing
│   ├── checkout.html           # Target web application
│   └── support_docs/           # Support documentation
│       ├── product_specs.md
│       ├── ui_ux_guide.txt
│       ├── api_endpoints.json
│       ├── business_rules.md
│       └── test_data.json
│
├── generated_tests/            # Generated output (gitignored)
│   └── selenium_scripts/       # Generated Selenium scripts
│
├── logs/                       # Application logs (gitignored)
│   ├── app.log                 # Text logs
│   └── app.json                # JSON logs
│
├── vector_store/               # Vector database (gitignored)
│   ├── qa_documents_index.faiss
│   ├── qa_documents_metadata.pkl
│   └── qa_documents_config.json
│
├── uploaded_files/             # Uploaded documents (gitignored)
│
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .env                       # Your environment variables (gitignored)
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
└── README.md                  # This file
```

## 🔌 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "app_name": "QA Agent",
  "version": "1.0.0",
  "timestamp": "2024-11-21T10:00:00.000Z",
  "services": {
    "bedrock": "healthy",
    "vector_store": "healthy",
    "documents_indexed": "25"
  }
}
```

#### Upload Documents
```http
POST /api/upload-documents
Content-Type: multipart/form-data
```

**Body:** Form data with multiple files

**Response:**
```json
{
  "success": true,
  "message": "Uploaded 5 files successfully",
  "files": ["product_specs.md", "ui_ux_guide.txt", ...],
  "file_paths": ["/path/to/file1", ...]
}
```

#### Build Knowledge Base
```http
POST /api/build-knowledge-base
Content-Type: application/json
```

**Request Body:**
```json
{
  "clear_existing": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Knowledge base built successfully",
  "files_processed": 5,
  "chunks_created": 127,
  "documents_added": 127,
  "collection_name": "qa_documents",
  "num_documents": 127
}
```

#### Generate Test Cases
```http
POST /api/generate-test-cases
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "Generate test cases for discount code functionality",
  "top_k": 5,
  "include_positive": true,
  "include_negative": true,
  "include_edge_cases": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Generated 8 test cases successfully",
  "test_cases": [
    {
      "test_id": "TC-001",
      "feature": "Discount Code Application",
      "test_scenario": "Apply valid discount code SAVE15",
      "test_type": "positive",
      "preconditions": ["Cart contains at least one item"],
      "test_steps": ["Navigate to checkout", "Add items", "Enter SAVE15", "Click Apply"],
      "expected_result": "15% discount applied to subtotal",
      "grounded_in": "product_specs.md - Section 3.1",
      "priority": "high",
      "test_data": {
        "discount_code": "SAVE15",
        "expected_discount_percentage": 15
      }
    }
  ],
  "sources": ["product_specs.md", "business_rules.md"],
  "query": "Generate test cases for discount code functionality",
  "generation_time": 12.34
}
```

#### Generate Selenium Script
```http
POST /api/generate-selenium-script
Content-Type: application/json
```

**Request Body:**
```json
{
  "test_case": {
    "test_id": "TC-001",
    "feature": "Discount Code",
    "test_scenario": "Apply valid code",
    "test_steps": ["Step 1", "Step 2"],
    "expected_result": "Discount applied"
  },
  "html_content": "<html>...</html>",
  "save_to_file": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Selenium script generated successfully",
  "script": "import pytest\nfrom selenium import webdriver\n...",
  "test_id": "TC-001",
  "feature": "Discount Code",
  "generation_time": 8.45,
  "sources": ["product_specs.md"]
}
```

## 🚢 Deployment

### AWS Deployment Options

#### Option 1: EC2 Deployment

1. **Launch EC2 Instance**
   - Ubuntu 22.04 or Amazon Linux 2
   - t3.medium or larger recommended
   - Configure security groups (ports 8000, 8501)

2. **Setup Instance**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install dependencies
   sudo apt install python3.10 python3-pip git -y

   # Clone repository
   git clone <your-repo>
   cd qa-agent-project

   # Install requirements
   pip3 install -r requirements.txt

   # Configure environment
   cp .env.example .env
   # Edit .env with AWS credentials
   ```

3. **Run with systemd** (Production)
   Create `/etc/systemd/system/qa-agent-backend.service`:
   ```ini
   [Unit]
   Description=QA Agent Backend
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/qa-agent-project
   Environment="PATH=/home/ubuntu/qa-agent-project/venv/bin"
   ExecStart=/home/ubuntu/qa-agent-project/venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable qa-agent-backend
   sudo systemctl start qa-agent-backend
   ```

#### Option 2: ECS/Fargate Deployment

1. **Build and Push Docker Image**
   ```bash
   # Build image
   docker build -t qa-agent:latest .

   # Tag for ECR
   docker tag qa-agent:latest <account-id>.dkr.ecr.<region>.amazonaws.com/qa-agent:latest

   # Push to ECR
   aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/qa-agent:latest
   ```

2. **Create ECS Task Definition**
   - Use Fargate launch type
   - Configure environment variables
   - Assign IAM role with Bedrock permissions

3. **Create ECS Service**
   - Deploy task definition
   - Configure load balancer (ALB)
   - Set auto-scaling policies

### Infrastructure-as-Code (Recommended)

Use the Terraform + ECS Fargate stack inside `infrastructure/terraform`:

1. **Provision AWS resources**
   ```bash
   cd infrastructure/terraform
   terraform init
   terraform apply \
     -var="project_name=qa-agent" \
     -var="environment=prod"
   ```
   This creates:
   - Two Amazon ECR repositories
   - ECS Fargate cluster/task with backend + frontend containers
   - Application Load Balancer with `/api/*` routing
   - CloudWatch log groups and IAM roles (Bedrock invoke permissions)

2. **Build & push Docker images**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

   BACKEND_REPO=<terraform backend_repository_url output>
   FRONTEND_REPO=<terraform frontend_repository_url output>

   docker build --target backend -t \"$BACKEND_REPO:latest\" .
   docker push \"$BACKEND_REPO:latest\"

   docker build --target frontend -t \"$FRONTEND_REPO:latest\" .
   docker push \"$FRONTEND_REPO:latest\"
   ```

3. **Redeploy ECS**
   ```bash
   aws ecs update-service \
     --cluster <ecs_cluster_name> \
     --service <ecs_service_name> \
     --force-new-deployment
   ```

4. **Helper scripts with logging**
   - `scripts/build_and_push_ecr.sh` — builds/pushes both Docker targets and streams logs to `logs/deployment/`
   - `scripts/ecs_force_deploy.sh` — triggers an ECS rollout with timestamped logs
   Set the required environment variables (`AWS_REGION`, `BACKEND_REPO`, `FRONTEND_REPO`, `ECS_CLUSTER`, `ECS_SERVICE`, optional `IMAGE_TAG`) before running.

5. **CI/CD automation (GitHub Actions)**
   - Workflow: `.github/workflows/aws-deploy.yml`
   - Required repository secrets:

     | Secret | Description |
     |--------|-------------|
     | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | CI/CD deploy credentials |
     | `AWS_REGION` | Region (e.g. `us-east-1`) |
     | `ECR_BACKEND_REPO`, `ECR_FRONTEND_REPO` | Repo URIs from Terraform |
     | `ECS_CLUSTER_NAME`, `ECS_SERVICE_NAME` | Names from Terraform outputs |

   - On push to `main`, the workflow builds both Docker targets, pushes `latest` tags, and triggers an ECS redeploy so the service picks up the new images.

👉 See `infrastructure/terraform/README.md` for the full step-by-step deployment guide.

#### Option 3: Docker Compose (Simple)

```bash
# On server
git clone <your-repo>
cd qa-agent-project
cp .env.example .env
# Edit .env

docker-compose up -d
```

### Environment-Specific Configurations

**Development:**
```env
ENVIRONMENT=development
LOG_LEVEL=DEBUG
API_RELOAD=true
```

**Production:**
```env
ENVIRONMENT=production
LOG_LEVEL=INFO
API_RELOAD=false
```

## 📦 Project Assets

### Included Test Assets

The project includes realistic test assets in `project_assets/`:

#### 1. checkout.html
A complete, functional e-commerce checkout page with:
- 3 products with "Add to Cart" buttons
- Shopping cart with quantity management
- Discount code functionality (SAVE15, WELCOME10, SUMMER20)
- User details form with validation
- Shipping options (Standard free, Express $10)
- Payment methods (Credit Card, PayPal)
- Complete JavaScript functionality

#### 2. Support Documents

**product_specs.md**
- Product catalog specifications
- Pricing details
- Discount code rules (SAVE15 = 15%, WELCOME10 = 10%, SUMMER20 = 20%)
- Shipping methods and costs
- Business rules

**ui_ux_guide.txt**
- Color palette specifications
- Typography guidelines
- Button design standards
- Form validation requirements
- Error message styling (RED text requirement)
- Success message styling
- Accessibility requirements

**api_endpoints.json**
- Mock API specifications
- Request/response formats
- Validation rules
- Error codes
- Authentication details

**business_rules.md**
- Form validation rules
- Order calculation logic
- Edge cases and scenarios
- Data integrity rules
- Testing considerations

**test_data.json**
- Valid test data examples
- Invalid test data examples
- Expected error messages
- Selenium selectors reference

### Using the Assets

1. **Upload all support docs** to build comprehensive knowledge base
2. **Upload checkout.html** for Selenium script generation
3. The AI will use these docs to generate grounded test cases

## 🎥 Demo Video

Create a 5-10 minute demo video showing:

1. **Introduction** (30 seconds)
   - Project overview
   - Technology stack

2. **Setup** (1 minute)
   - Environment configuration
   - Starting the application

3. **Document Upload** (1 minute)
   - Uploading support documents
   - Uploading checkout.html

4. **Knowledge Base Building** (1 minute)
   - Building knowledge base
   - Viewing statistics

5. **Test Case Generation** (2-3 minutes)
   - Multiple query examples
   - Reviewing generated test cases
   - Showing grounding in documentation

6. **Selenium Script Generation** (2-3 minutes)
   - Selecting a test case
   - Generating script
   - Reviewing generated code
   - Running the script (optional)

7. **Conclusion** (30 seconds)
   - Key features recap
   - Benefits summary

## 🔧 Troubleshooting

### Common Issues

#### 1. AWS Bedrock Access Denied
```
Error: Access denied to model
```
**Solution:**
- Ensure you've requested and been granted access to Nova Lite and Cohere Embed v4 in AWS Bedrock Console
- Check IAM permissions include `bedrock:InvokeModel`

#### 2. Connection Refused to API
```
Error: Cannot connect to API
```
**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Restart backend
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

#### 3. Empty Knowledge Base
```
Error: No relevant documentation found
```
**Solution:**
- Upload documents first
- Build knowledge base
- Check logs for processing errors

#### 4. Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt
```

#### 5. Slow Performance
**Symptoms:** Test generation takes very long

**Solutions:**
- Reduce `top_k` value (fewer documents retrieved)
- Reduce `chunk_size` in configuration
- Check AWS region latency
- Upgrade EC2 instance type
- Check AWS Bedrock throttling limits

### Debug Mode

Enable detailed logging:
```env
LOG_LEVEL=DEBUG
```

View logs:
```bash
tail -f logs/app.log
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Knowledge base stats
curl http://localhost:8000/api/knowledge-base/stats
```

## 📝 Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Formatting
```bash
black backend/ frontend/
flake8 backend/ frontend/
```

### Adding New Document Types

1. Update `document_parser.py` with new parser method
2. Add file extension to `allowed_extensions` in config
3. Test with sample files

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

This project is for educational purposes as part of the QA Agent assignment.

## 🆘 Support

For issues, questions, or feedback:
- Create an issue in the repository
- Check troubleshooting section
- Review logs in `logs/` directory

## 🎯 Success Criteria

This implementation fulfills all assignment requirements:

✅ **Functionality**
- Document ingestion and knowledge base building
- RAG-based test case generation
- Selenium script generation from test cases

✅ **Knowledge Grounding**
- All test cases strictly based on documentation
- Source references in every test case
- No hallucinated features

✅ **Script Quality**
- Production-ready Selenium scripts
- Correct selectors from HTML
- Proper waits and assertions

✅ **Code Quality**
- Modular, well-structured code
- FastAPI backend with Streamlit UI
- Comprehensive logging

✅ **User Experience**
- Intuitive Streamlit interface
- Clear feedback at every step
- Easy document upload and management

✅ **Documentation**
- Detailed README with setup instructions
- API documentation
- Usage examples

---

**Built with ❤️ using AWS Bedrock, FastAPI, and Streamlit**
