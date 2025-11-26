#!/bin/bash
# Deploy QA Agent to AWS EC2

echo "🚀 QA Agent - AWS Deployment Script"
echo "===================================="
echo ""

# Check if EC2 host is provided
if [ -z "$1" ]; then
    echo "Usage: ./deploy_to_aws.sh <ec2-host> <key-file>"
    echo "Example: ./deploy_to_aws.sh ubuntu@54.123.45.67 ~/.ssh/my-key.pem"
    exit 1
fi

EC2_HOST=$1
KEY_FILE=${2:-~/.ssh/id_rsa}

echo "📍 Target: $EC2_HOST"
echo "🔑 Key: $KEY_FILE"
echo ""

# Test connection
echo "🔍 Testing SSH connection..."
ssh -i $KEY_FILE -o ConnectTimeout=5 $EC2_HOST "echo '✅ SSH connection successful'" || {
    echo "❌ Cannot connect to EC2 instance"
    exit 1
}

# Upload project files
echo ""
echo "📦 Uploading project files..."
rsync -avz -e "ssh -i $KEY_FILE" \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude 'vector_store' \
    --exclude 'logs' \
    --exclude 'uploaded_files' \
    --exclude 'generated_tests' \
    . $EC2_HOST:~/qa-agent-project/

# Setup and start on EC2
echo ""
echo "🔧 Setting up on EC2..."
ssh -i $KEY_FILE $EC2_HOST << 'ENDSSH'
cd ~/qa-agent-project

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    sudo apt update
    sudo apt install -y docker.io docker-compose git
    sudo usermod -aG docker ubuntu
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Check .env file
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your AWS credentials"
    exit 1
fi

# Start application
echo "🚀 Starting QA Agent..."
docker-compose down 2>/dev/null
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "===================================="
echo "✅ Deployment Complete!"
echo "===================================="
echo ""
echo "Access your application:"
echo "  Streamlit UI:  http://$(curl -s ifconfig.me):8501"
echo "  API Docs:      http://$(curl -s ifconfig.me):8000/docs"
echo "  Health Check:  http://$(curl -s ifconfig.me):8000/health"
echo ""
echo "To view logs:"
echo "  ssh -i $KEY_FILE $EC2_HOST 'cd ~/qa-agent-project && docker-compose logs -f'"
echo ""
echo "To stop:"
echo "  ssh -i $KEY_FILE $EC2_HOST 'cd ~/qa-agent-project && docker-compose down'"
echo "===================================="
ENDSSH

echo ""
echo "✅ Deployment script completed!"
