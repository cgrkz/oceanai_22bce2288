# Quick Start Guide

Get up and running with QA Agent in 5 minutes!

## Prerequisites

✅ Python 3.10+
✅ AWS Bedrock access (Nova Lite + Cohere Embed v4)
✅ AWS credentials (Access Key ID & Secret Key)

## Quick Setup

### 1. Clone & Setup (2 minutes)

```bash
# Clone repository
cd qa-agent-project

# Copy environment file
cp .env.example .env
```

Edit `.env` and add your AWS credentials:
```env
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=us-east-1
```

### 2. Start Application (1 minute)

**On macOS/Linux:**
```bash
./start.sh
```

**On Windows:**
```bash
start.bat
```

**Or manually:**
```bash
# Terminal 1 - Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload

# Terminal 2 - Frontend
streamlit run frontend/streamlit_app.py
```

### 3. Access Application

- 🌐 **Streamlit UI**: http://localhost:8501
- 📚 **API Docs**: http://localhost:8000/docs

## Using the Application (2 minutes)

### Step 1: Upload Documents (30 seconds)

1. Go to **📁 Upload Documents**
2. Upload files from `project_assets/support_docs/`:
   - `product_specs.md`
   - `ui_ux_guide.txt`
   - `api_endpoints.json`
   - `business_rules.md`
   - `test_data.json`
3. Click **Upload Files**

### Step 2: Build Knowledge Base (30 seconds)

1. Go to **🧠 Build Knowledge Base**
2. Upload `project_assets/checkout.html`
3. Keep "Clear existing knowledge base" checked
4. Click **Build Knowledge Base**
5. Wait ~1-2 minutes for processing

### Step 3: Generate Test Cases (30 seconds)

1. Go to **✍️ Generate Test Cases**
2. Enter query: `Generate test cases for discount code functionality`
3. Click **Generate Test Cases**
4. Wait ~30 seconds
5. Review generated test cases

### Step 4: Generate Selenium Script (30 seconds)

1. Go to **🔧 Generate Selenium Scripts**
2. Select a test case from dropdown
3. Enable "Include HTML context"
4. Click **Generate Selenium Script**
5. Download or copy the script

## Example Queries

Try these queries for test case generation:

```
✅ Generate test cases for discount code functionality
✅ Generate test cases for form validation
✅ Generate test cases for shopping cart operations
✅ Generate test cases for checkout flow
✅ Generate negative test cases for invalid inputs
✅ Generate edge case tests for boundary conditions
```

## Troubleshooting

### Can't connect to API?
```bash
# Check if backend is running
curl http://localhost:8000/health
```

### AWS credentials not working?
- Verify credentials in `.env`
- Check Bedrock model access in AWS Console
- Ensure region is correct (default: us-east-1)

### Empty knowledge base?
- Make sure you uploaded documents
- Click "Build Knowledge Base" button
- Check logs: `tail -f logs/app.log`

## Next Steps

📖 Read the full [README.md](README.md) for:
- Detailed API documentation
- AWS deployment guide
- Advanced configuration options
- Development guidelines

## Need Help?

- Check [README.md](README.md) Troubleshooting section
- Review logs in `logs/` directory
- Check API docs: http://localhost:8000/docs

---

**Ready to generate some test cases?** 🚀
