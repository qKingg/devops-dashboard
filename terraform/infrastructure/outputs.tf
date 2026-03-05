#outputs

output "alb_dns_name" {
  description = "DNS name of the application load balancer"
  value = aws_lb.app_lb.dns_name
}

output "ecr_repo_url" {
  description = "URL of the ECR repository"
  value = aws_ecr_repository.app_repo.repository_url
}

output "ecr_repo_arn" {
  description = "ARN of the ECR repository"
  value = aws_ecr_repository.app_repo.arn
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value = aws_ecs_cluster.default.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value = aws_ecs_service.default.name
}

output "rds_endpoint" {
  description = "Endpoint of the RDS instance"
  value = aws_db_instance.default.endpoint
}

output "rds_password_ssm_parameter" {
  description = "SSM parameter name for the RDS password"
  value = aws_ssm_parameter.db_password.name
}