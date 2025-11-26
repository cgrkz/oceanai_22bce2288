terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

locals {
  name_prefix        = "${var.project_name}-${var.environment}"
  backend_image      = "${aws_ecr_repository.backend.repository_url}:${var.image_tag}"
  frontend_image     = "${aws_ecr_repository.frontend.repository_url}:${var.image_tag}"
  streamlit_env_vars = [
    {
      name  = "API_BASE_URL"
      value = "http://127.0.0.1:8000"
    },
    {
      name  = "STREAMLIT_SERVER_PORT"
      value = tostring(var.frontend_container_port)
    }
  ]
  backend_env_vars = [
    {
      name  = "API_HOST"
      value = "0.0.0.0"
    },
    {
      name  = "API_PORT"
      value = tostring(var.backend_container_port)
    },
    {
      name  = "AWS_REGION"
      value = var.aws_region
    },
    {
      name  = "BEDROCK_LLM_MODEL_ID"
      value = var.bedrock_llm_model_id
    },
    {
      name  = "BEDROCK_EMBEDDING_MODEL_ID"
      value = var.bedrock_embedding_model_id
    }
  ]
}

resource "aws_ecr_repository" "backend" {
  name                 = "${var.project_name}-backend"
  image_tag_mutability = "MUTABLE"
  force_delete         = false
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "frontend" {
  name                 = "${var.project_name}-frontend"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${local.name_prefix}-backend"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/ecs/${local.name_prefix}-frontend"
  retention_in_days = 30
}

resource "aws_ecs_cluster" "this" {
  name = "${local.name_prefix}-cluster"
}

resource "aws_iam_role" "task_execution" {
  name = "${local.name_prefix}-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role" "task_role" {
  name = "${local.name_prefix}-task-role"
  assume_role_policy = aws_iam_role.task_execution.assume_role_policy
}

resource "aws_iam_role_policy_attachment" "task_execution" {
  role       = aws_iam_role.task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "bedrock" {
  name = "${local.name_prefix}-bedrock-policy"
  role = aws_iam_role.task_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_security_group" "alb" {
  name        = "${local.name_prefix}-alb"
  description = "ALB security group"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.alb_ingress_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs" {
  name        = "${local.name_prefix}-ecs"
  description = "ECS tasks"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port       = var.frontend_container_port
    to_port         = var.frontend_container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  ingress {
    from_port       = var.backend_container_port
    to_port         = var.backend_container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "this" {
  name               = "${local.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = data.aws_subnets.default.ids
}

resource "aws_lb_target_group" "frontend" {
  name        = "${local.name_prefix}-frontend"
  port        = var.frontend_container_port
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = data.aws_vpc.default.id
  health_check {
    path                = "/_stcore/health"
    matcher             = "200-399"
    healthy_threshold   = 2
    unhealthy_threshold = 5
    interval            = 30
  }
}

resource "aws_lb_target_group" "backend" {
  name        = "${local.name_prefix}-backend"
  port        = var.backend_container_port
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = data.aws_vpc.default.id
  health_check {
    path = "/health"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}

resource "aws_lb_listener_rule" "api" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    path_pattern {
      values = ["/api*", "/docs*", "/redoc*"]
    }
  }
}

resource "aws_ecs_task_definition" "this" {
  family                   = "${local.name_prefix}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = tostring(var.task_cpu)
  memory                   = tostring(var.task_memory)
  execution_role_arn       = aws_iam_role.task_execution.arn
  task_role_arn            = aws_iam_role.task_role.arn

  container_definitions = jsonencode([
    {
      name      = "qa-backend"
      image     = local.backend_image
      essential = true
      portMappings = [
        {
          containerPort = var.backend_container_port
          hostPort       = var.backend_container_port
          protocol       = "tcp"
        }
      ]
      environment = local.backend_env_vars
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.backend.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "backend"
        }
      }
    },
    {
      name      = "qa-frontend"
      image     = local.frontend_image
      essential = true
      portMappings = [
        {
          containerPort = var.frontend_container_port
          hostPort       = var.frontend_container_port
          protocol       = "tcp"
        }
      ]
      environment = local.streamlit_env_vars
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.frontend.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "frontend"
        }
      }
      dependsOn = [
        {
          containerName = "qa-backend"
          condition     = "START"
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "this" {
  name            = "${local.name_prefix}-service"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = data.aws_subnets.default.ids
    security_groups = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend.arn
    container_name   = "qa-frontend"
    container_port   = var.frontend_container_port
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "qa-backend"
    container_port   = var.backend_container_port
  }

  depends_on = [
    aws_lb_listener.http,
    aws_lb_listener_rule.api
  ]
}
