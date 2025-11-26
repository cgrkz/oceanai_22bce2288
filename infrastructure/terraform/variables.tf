variable "project_name" {
  description = "Name prefix for resources"
  type        = string
  default     = "qa-agent"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "prod"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "desired_count" {
  description = "Number of ECS tasks"
  type        = number
  default     = 1
}

variable "task_cpu" {
  description = "CPU units for Fargate task"
  type        = number
  default     = 1024
}

variable "task_memory" {
  description = "Memory (MB) for Fargate task"
  type        = number
  default     = 2048
}

variable "backend_container_port" {
  description = "Container port for FastAPI"
  type        = number
  default     = 8000
}

variable "frontend_container_port" {
  description = "Container port for Streamlit"
  type        = number
  default     = 8501
}

variable "alb_ingress_cidr" {
  description = "CIDR block allowed to hit ALB"
  type        = string
  default     = "0.0.0.0/0"
}

variable "image_tag" {
  description = "Image tag to deploy"
  type        = string
  default     = "latest"
}

variable "bedrock_llm_model_id" {
  description = "Bedrock LLM model ID"
  type        = string
  default     = "amazon.nova-lite-v1:0"
}

variable "bedrock_embedding_model_id" {
  description = "Bedrock embedding model ID"
  type        = string
  default     = "cohere.embed-v4:0"
}
