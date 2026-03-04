#load balancer module
resource "aws_lb" "app_lb" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

    tags = {
        Name = "${var.project_name}-alb"
    }
}

resource "aws_lb_target_group" "app_tg" {
  name     = "${var.project_name}-tg"
  port     = var.container_port
  protocol = "HTTP"
  target_type = "ip"
  vpc_id   = aws_vpc.main.id

    tags = {
        Name = "${var.project_name}-tg"
    }
}

