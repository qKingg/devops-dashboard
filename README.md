# AWS Cloud Metrics Dashboard

Production-grade CloudWatch metrics dashboard built on ECS Fargate, with Terraform IaC, GitHub Actions CI/CD (OIDC), and automated monitoring. Deployed at dashboard.catalinpatrut.com


## Architecture

![Architecture Diagram](docs/devops-dashboard-architecture.svg)

## Tech Stack

| Category           | Tools                                                        |
|--------------------|--------------------------------------------------------------|
| **Application**    | Python, Flask, SQLAlchemy, Gunicorn, psycopg3                |
| **Infrastructure** | AWS (ECS Fargate, ALB, RDS PostgreSQL, VPC, Route53, ACM)    |
| **IaC**            | Terraform (S3 + DynamoDB remote state)                       |
| **CI/CD**          | GitHub Actions, OIDC auth, Trivy, ECR                        |
| **Monitoring**     | CloudWatch dashboards, CloudWatch alarms                     |
| **Security**       | OIDC (no static keys), private subnets, non-root containers, TLS 1.2/1.3, Secrets Manager |