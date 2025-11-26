# Terraform Deployment (AWS ECS Fargate)

This Terraform configuration creates a production-ready AWS stack for the QA Agent application:

- **ECR** repositories for backend & frontend images
- **ECS Fargate** cluster and service with both containers in one task
- **Application Load Balancer** with routing for Streamlit + API paths
- **CloudWatch Logs** for both containers
- **IAM roles** with Bedrock invoke permissions

## Prerequisites

1. Terraform >= 1.5.0
2. AWS CLI configured with deploy permissions (`ecs`, `ecr`, `iam`, `ec2`, `elasticloadbalancing`)
3. Docker + AWS credentials for building & pushing images

## Usage

```bash
cd infrastructure/terraform
terraform init
terraform plan -var="project_name=qa-agent" -var="environment=prod"
terraform apply -auto-approve
```

Outputs include:
- `alb_dns_name`
- `backend_repository_url`
- `frontend_repository_url`
- `ecs_cluster_name`
- `ecs_service_name`

## Build & Push Images

After Terraform creates the ECR repositories, build and push the Docker images:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Backend image
BACKEND_REPO=<backend_repository_url>
docker build --target backend -t "$BACKEND_REPO:latest" .
docker push "$BACKEND_REPO:latest"

# Frontend image
docker build --target frontend -t "$FRONTEND_REPO:latest" .
docker push "$FRONTEND_REPO:latest"
```

Then force a deployment so ECS pulls the new images:

```bash
aws ecs update-service \
  --cluster <ecs_cluster_name> \
  --service <ecs_service_name> \
  --force-new-deployment
```

## Configuration

Adjust settings in `variables.tf` as needed:

| Variable | Description | Default |
|----------|-------------|---------|
| `project_name` | Resource/name prefix | `qa-agent` |
| `environment` | Environment label | `prod` |
| `aws_region` | AWS region | `us-east-1` |
| `desired_count` | ECS task count | `1` |
| `alb_ingress_cidr` | Allowed CIDR to ALB | `0.0.0.0/0` |
| `image_tag` | Docker image tag | `latest` |

## Networking Notes

- Uses the default VPC + subnets for simplicity.
- ECS tasks receive public IPs to access AWS Bedrock endpoints.
- Load balancer exposes HTTP/80:
  - `/` → Streamlit frontend
  - `/api/*`, `/docs*`, `/redoc*` → FastAPI backend

## IAM Notes

The ECS task role grants permission to invoke AWS Bedrock models so you do **not** need to bake AWS keys into the container. Locally you can still use `.env`, but in AWS the discovery chain uses the task role automatically.
