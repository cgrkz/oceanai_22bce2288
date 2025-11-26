# AWS Deployment Guide for QA Agent

## Current Status

🖥️ **Running Locally**: Yes (on your Mac)
☁️ **Deployed to AWS**: No (not yet)
🔌 **AWS Bedrock**: Connected and working

---

## Quick Deploy to AWS (15 minutes)

### Step 1: Launch EC2 Instance

1. **Go to AWS Console**
   - Navigate to https://console.aws.amazon.com/ec2/

2. **Launch Instance**
   - Click "Launch Instance"
   - Name: `qa-agent-server`
   - AMI: Ubuntu Server 22.04 LTS
   - Instance type: `t3.medium` (2 vCPU, 4GB RAM)
   - Key pair: Create new or use existing
   - Storage: 20GB gp3

3. **Configure Security Group**
   - Allow SSH (port 22) from your IP
   - Allow Custom TCP (port 8000) from anywhere (0.0.0.0/0)
   - Allow Custom TCP (port 8501) from anywhere (0.0.0.0/0)

4. **Launch Instance**
   - Click "Launch Instance"
   - Wait for instance to be "Running"
   - Note the Public IPv4 address

### Step 2: Deploy Using Script

```bash
# On your Mac, in the project directory:
cd /path/to/your/qa-agent-project

# Deploy to EC2 (replace with your values)
./deploy_to_aws.sh ubuntu@YOUR_EC2_IP ~/.ssh/your-key.pem

# Example:
# ./deploy_to_aws.sh ubuntu@54.123.45.67 ~/.ssh/qa-agent-key.pem
```

### Step 3: Access Your Application

```
Streamlit UI:  http://YOUR_EC2_IP:8501
API Docs:      http://YOUR_EC2_IP:8000/docs
Health Check:  http://YOUR_EC2_IP:8000/health
```

---

## Manual Deployment (If Script Fails)

### 1. Connect to EC2

```bash
ssh -i ~/.ssh/your-key.pem ubuntu@YOUR_EC2_IP
```

### 2. Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io docker-compose git

# Add user to docker group
sudo usermod -aG docker ubuntu

# Log out and back in
exit
ssh -i ~/.ssh/your-key.pem ubuntu@YOUR_EC2_IP
```

### 3. Upload Project

**Option A: Using Git (Recommended)**
```bash
# On EC2:
git clone <your-repo-url>
cd qa-agent-project
```

**Option B: Using SCP**
```bash
# On your Mac:
cd /path/to/your/qa-agent-project
tar -czf qa-agent.tar.gz --exclude='venv' --exclude='__pycache__' --exclude='vector_store' .
scp -i ~/.ssh/your-key.pem qa-agent.tar.gz ubuntu@YOUR_EC2_IP:~
ssh -i ~/.ssh/your-key.pem ubuntu@YOUR_EC2_IP
tar -xzf qa-agent.tar.gz -C qa-agent-project
cd qa-agent-project
```

### 4. Configure Environment

```bash
# On EC2:
cd ~/qa-agent-project

# Copy and edit .env
cp .env.example .env
nano .env

# Add your AWS credentials:
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# AWS_REGION=us-east-1
```

### 5. Start Application

```bash
# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 6. Test Deployment

```bash
# Check health endpoint
curl http://localhost:8000/health

# From your browser:
http://YOUR_EC2_IP:8501
```

---

## Cost Estimate

### EC2 Instance (t3.medium)
- **On-Demand**: ~$0.0416/hour = ~$30/month (if running 24/7)
- **Spot Instance**: ~$0.0125/hour = ~$9/month

### AWS Bedrock Usage
- **Nova Lite**: Pay per request (~$0.01 per 1000 tokens)
- **Cohere Embed v4**: Pay per request (~$0.0002 per 1000 tokens)

**Estimated Monthly Cost for Demo/Testing**:
- EC2: $30/month (on-demand) or $9/month (spot)
- Bedrock: $5-10/month (light usage)
- **Total**: ~$35-40/month (on-demand) or ~$15-20/month (spot)

---

## Production Deployment Options

### Option 1: EC2 with Auto-Scaling
```
✅ Pros: Simple, full control, scalable
❌ Cons: Need to manage servers
💰 Cost: ~$30-100/month
```

### Option 2: ECS Fargate
```
✅ Pros: Serverless, auto-scaling, managed
❌ Cons: More complex setup
💰 Cost: ~$40-80/month
```

### Option 3: AWS App Runner
```
✅ Pros: Fully managed, auto-scaling
✅ Easiest deployment from container
💰 Cost: ~$25-50/month
```

---

## Monitoring and Maintenance

### View Logs
```bash
ssh -i ~/.ssh/your-key.pem ubuntu@YOUR_EC2_IP
cd ~/qa-agent-project
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Services
```bash
docker-compose restart
```

### Update Application
```bash
# Pull latest changes
git pull

# Restart
docker-compose down
docker-compose up -d --build
```

### Stop Application
```bash
docker-compose down
```

---

## Security Recommendations

### 1. Restrict Security Group
Instead of allowing 0.0.0.0/0, restrict to your IP:
```
Port 8501 (Streamlit): Your IP only
Port 8000 (API): Your IP only
Port 22 (SSH): Your IP only
```

### 2. Use IAM Role (Production)
Instead of AWS credentials in .env:
1. Create IAM role with Bedrock permissions
2. Attach to EC2 instance
3. Remove credentials from .env

### 3. Enable HTTPS
Use AWS Application Load Balancer with SSL certificate

### 4. Set Up Backups
- Enable EC2 snapshots
- Back up vector_store directory
- Export generated tests regularly

---

## Troubleshooting

### Can't Connect to EC2
```bash
# Check security group allows your IP
# Check instance is running
aws ec2 describe-instances --instance-ids i-xxxxx

# Try verbose SSH
ssh -vvv -i ~/.ssh/your-key.pem ubuntu@YOUR_EC2_IP
```

### Docker Not Working
```bash
# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Check user in docker group
groups ubuntu
```

### Application Not Starting
```bash
# Check logs
docker-compose logs

# Check .env file
cat .env

# Restart services
docker-compose restart
```

### Can't Access from Browser
```bash
# Check services are running
docker-compose ps

# Check ports are listening
sudo netstat -tlnp | grep -E '8000|8501'

# Check security group rules in AWS Console
```

---

## Alternative: AWS App Runner (Easiest)

If you want the simplest deployment:

### 1. Push to Docker Hub
```bash
cd /path/to/your/qa-agent-project

# Build and push
docker build -t your-username/qa-agent:latest .
docker push your-username/qa-agent:latest
```

### 2. Create App Runner Service
1. Go to AWS App Runner console
2. Create service
3. Source: Container registry → Docker Hub
4. Image: your-username/qa-agent:latest
5. Port: 8501
6. Environment variables: Add AWS credentials
7. Create service

**Pros**: Fully managed, auto-scaling, HTTPS included
**Cons**: More expensive (~$25-50/month)

---

## Next Steps

### For Demo (Quick)
1. Use local deployment: `./start.sh`
2. Record demo video showing local setup
3. Deploy to AWS after demo if needed

### For Production
1. Deploy to AWS EC2 using script
2. Set up monitoring (CloudWatch)
3. Configure domain name
4. Enable HTTPS with ALB
5. Set up CI/CD pipeline

---

## Current Recommendation

**For Assignment Demo**: Keep it **LOCAL**
- ✅ Faster to demo
- ✅ No additional costs
- ✅ Easier to debug
- ✅ Already tested and working

**After Demo**: Deploy to AWS
- Use the deployment script provided
- Or follow manual steps above

---

## Summary

| Deployment | Status | Action |
|------------|--------|--------|
| **Local (Mac)** | ✅ Working | Use `./start.sh` |
| **AWS EC2** | ⏳ Ready | Use `./deploy_to_aws.sh` |
| **AWS ECS** | ⏳ Ready | Follow ECS guide |
| **AWS App Runner** | ⏳ Ready | Push to registry |

**Current Status**: Running locally, AWS Bedrock connected, ready to deploy

**Recommendation**: Run demo locally first, then deploy to AWS if needed.

---

Need help deploying? Let me know which option you prefer!
