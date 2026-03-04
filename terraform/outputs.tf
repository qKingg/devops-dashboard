#outputs

output "alb_dns_name" {
  description = "DNS name of the application load balancer"
  value = aws_lb.app_lb.dns_name
}

output "ecr_repo_url" {
  description = "URL of the ECR repository"
  value = aws_ecr_repository.app_repo.repository_url
}

output "rds_endpoint" {
  description = "Endpoint of the RDS instance"
  value = aws_db_instance.default.endpoint
}

output "rds_password_ssm_parameter" {
  description = "SSM parameter name for the RDS password"
  value = aws_ssm_parameter.db_password.name
}