variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "devops-dashboard"
}

variable "environment" {
  description = "Project environment"
  type        = string
  default     = "dev"
}

variable "ecr_repository_arn" {
  description = "ARN of the ECR repository (from infrastructure outputs)"
  type        = string
  default       = "arn:aws:ecr:eu-central-1:457200661628:repository/devops-dashboard-repo"
}

variable "ecs_cluster_name" {
  description = "Name of the ECS cluster (from infrastructure outputs)"
  type        = string
  default     = "devops-dashboard-cluster"
}

variable "ecs_service_name" {
  description = "Name of the ECS service (from infrastructure outputs)"
  type        = string
  default     = "devops-dashboard-service"
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = "qKingg"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "devops-dashboard"
}

variable "ecs_task_execution_role_arn" {
  description = "ARN of the ECS task execution role (for PassRole scoping)"
  type        = string
  default     = "arn:aws:iam::457200661628:role/devops-dashboard-ecs-task-execution-role"
}

variable "ecs_task_role_arn" {
  description = "ARN of the ECS task role (for PassRole scoping)"
  type        = string
  default     = "arn:aws:iam::457200661628:role/devops-dashboard-ecs-task-role"
}
