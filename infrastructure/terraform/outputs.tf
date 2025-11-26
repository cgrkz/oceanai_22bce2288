output "alb_dns_name" {
  description = "Public DNS of the load balancer"
  value       = aws_lb.this.dns_name
}

output "backend_repository_url" {
  description = "ECR repo for backend"
  value       = aws_ecr_repository.backend.repository_url
}

output "frontend_repository_url" {
  description = "ECR repo for frontend"
  value       = aws_ecr_repository.frontend.repository_url
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.this.name
  description = "Name of ECS cluster"
}

output "ecs_service_name" {
  value       = aws_ecs_service.this.name
  description = "Name of ECS service"
}
