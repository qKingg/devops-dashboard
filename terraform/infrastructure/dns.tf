data "aws_route53_zone" "main" {
  name         = var.domain_name
  private_zone = false
}

#Generate ACM certificate
resource "aws_acm_certificate" "cert" {
  domain_name       =  "dashboard.${var.domain_name}"
  validation_method = "DNS"

  tags = {
    Name        = "${var.project_name}-cert"
    Environment = var.environment
  }

  lifecycle {
    create_before_destroy = true
  }
}

#validation record for ACM certificate
resource "aws_route53_record" "cert_validation" {
  for_each = {for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => {
    name   = dvo.resource_record_name
    type   = dvo.resource_record_type
    record = dvo.resource_record_value
  }}

  zone_id = data.aws_route53_zone.main.zone_id
  name    = each.value.name
  type    = each.value.type
  records = [each.value.record]
  allow_overwrite = true

  ttl = 60
}

# Validate the ACM certificate with Route53 records
resource "aws_acm_certificate_validation" "cert" {
  certificate_arn = aws_acm_certificate.cert.arn

  timeouts {
    create = "5m"
  }

  depends_on = [aws_route53_record.cert_validation]
}

resource "aws_route53_record" "alb_alias" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "dashboard.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_lb.app_lb.dns_name
    zone_id                = aws_lb.app_lb.zone_id
    evaluate_target_health = true
  }
}