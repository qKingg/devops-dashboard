#alarms

resource "aws_cloudwatch_metric_alarm" "alb-server-error" {
  alarm_name          = "${var.project_name}-alb-server-error"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "HTTPCode_ELB_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 10
  treat_missing_data   = "notBreaching"

  dimensions = {
    LoadBalancer = aws_lb.app_lb.arn_suffix
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}

#ecs high cpu
resource "aws_cloudwatch_metric_alarm" "ecs-high-cpu" {
  alarm_name          = "${var.project_name}-ecs-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 80

  dimensions = {
    ClusterName = aws_ecs_cluster.default.name
    ServiceName = aws_ecs_service.default.name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}

#ecs high mem
resource "aws_cloudwatch_metric_alarm" "ecs-high-mem" {
  alarm_name          = "${var.project_name}-ecs-high-mem"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 80

  dimensions = {
    ClusterName = aws_ecs_cluster.default.name
    ServiceName = aws_ecs_service.default.name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}

#rds free storage low
resource "aws_cloudwatch_metric_alarm" "rds-low-storage" {
  alarm_name          = "${var.project_name}-rds-low-storage"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 60
  statistic           = "Average"
  threshold           = 10737418240 # 10 GB

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.default.identifier
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-dashboard"
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "HTTPCode_ELB_5XX_Count", "LoadBalancer", aws_lb.app_lb.arn_suffix],
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", aws_lb.app_lb.arn_suffix]
          ]
          period = 60
          stat   = "Sum"
          region = var.aws_region
          title  = "ALB 5XX Errors"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", aws_ecs_cluster.default.name, "ServiceName", aws_ecs_service.default.name],
            ["AWS/ECS", "MemoryUtilization", "ClusterName", aws_ecs_cluster.default.name, "ServiceName", aws_ecs_service.default.name]
          ]
          period = 60
          stat   = "Average"
          region = var.aws_region
          title  = "ECS CPU & Memory Utilization"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 24
        height = 6
        properties = {
          metrics = [
            ["AWS/RDS", "FreeStorageSpace", "DBInstanceIdentifier", aws_db_instance.default.identifier]
          ]
          period = 60
          stat   = "Average"
          region = var.aws_region
          title  = "RDS Free Storage Space"
        }
      }
    ]
  })
}