resource "aws_ecs_cluster" "default" {
  name = "${var.project_name}-cluster"
}

resource "aws_cloudwatch_log_group" "default" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 7
}

resource "aws_ecs_task_definition" "default" {
  family                   = "${var.project_name}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.container_cpu
  memory                   = var.container_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn


  lifecycle {
    ignore_changes = [container_definitions]
  }

  container_definitions = jsonencode([
    {
      name  = "${var.project_name}-container"
      image = "${aws_ecr_repository.app_repo.repository_url}:ab32303489bc0996ae91f6e59f07e390b666c5e7"
      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]
      environment = [{
        name  = "DATABASE_URL"
        value = "postgresql+psycopg://${var.db_username}:${random_password.db_password.result}@${aws_db_instance.default.endpoint}/${var.db_name}"
      }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.default.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "${var.project_name}-logs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "default" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.default.id
  task_definition = aws_ecs_task_definition.default.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  depends_on = [aws_lb_listener.app_listener]

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  #load balancer target group ARN, container name
  load_balancer {
    target_group_arn = aws_lb_target_group.app_tg.arn
    container_name   = "${var.project_name}-container"
    container_port   = var.container_port
  }

  lifecycle {
    ignore_changes = [task_definition]
  }

  tags = {
    Name = "${var.project_name}-service"
  }
}