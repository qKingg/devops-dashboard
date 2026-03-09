#!/usr/bin/env python3
"""
Collects CloudWatch metrics from AWS and POSTs them to the DevOps Dashboard API.

Metrics collected:
  - ECS CPUUtilization (%)
  - ECS MemoryUtilization (%)
  - RDS FreeStorageSpace (GB)
  - ALB 5XX error count
  - ALB RequestCount

Usage:
  pip install boto3 requests
  export APP_URL=https://catalinpatrut.com   # or http://localhost:5000
  export AWS_REGION=eu-central-1              # optional, defaults to eu-central-1
  python scripts/collect_metrics.py

Can be run as a cron job or scheduled Lambda.
"""

import os
import sys
from datetime import datetime, timedelta, timezone

import boto3
import requests

# --- Configuration ---
# APP_URL = os.getenv("APP_URL", "https://dashboard.catalinpatrut.com").rstrip("/")
APP_URL = os.getenv("APP_URL", "http://localhost:5000").rstrip("/")
AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
PROJECT_NAME = os.getenv("PROJECT_NAME", "devops-dashboard")

ECS_CLUSTER = f"{PROJECT_NAME}-cluster"
ECS_SERVICE = f"{PROJECT_NAME}-service"

METRICS_ENDPOINT = f"{APP_URL}/api/metrics"

cloudwatch = boto3.client("cloudwatch", region_name=AWS_REGION)


def get_metric(namespace, metric_name, dimensions, stat="Average", period=300):
    """Query a single CloudWatch metric and return the most recent data point."""
    now = datetime.now(timezone.utc)
    response = cloudwatch.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=now - timedelta(seconds=period),
        EndTime=now,
        Period=period,
        Statistics=[stat],
    )
    datapoints = response.get("Datapoints", [])
    if not datapoints:
        return None
    latest = max(datapoints, key=lambda dp: dp["Timestamp"])
    return latest[stat]


def collect_all_metrics():
    """Gather all CloudWatch metrics and return them as a list of dicts."""
    metrics = []

    # ECS CPU Utilization
    cpu = get_metric(
        namespace="AWS/ECS",
        metric_name="CPUUtilization",
        dimensions=[
            {"Name": "ClusterName", "Value": ECS_CLUSTER},
            {"Name": "ServiceName", "Value": ECS_SERVICE},
        ],
    )
    if cpu is not None:
        metrics.append({"metric_name": "ecs_cpu_utilization", "metric_value": round(cpu, 2), "unit": "%"})

    # ECS Memory Utilization
    mem = get_metric(
        namespace="AWS/ECS",
        metric_name="MemoryUtilization",
        dimensions=[
            {"Name": "ClusterName", "Value": ECS_CLUSTER},
            {"Name": "ServiceName", "Value": ECS_SERVICE},
        ],
    )
    if mem is not None:
        metrics.append({"metric_name": "ecs_memory_utilization", "metric_value": round(mem, 2), "unit": "%"})

    # RDS Free Storage Space (convert bytes -> GB)
    rds_instance_id = get_rds_instance_id()
    storage = None
    if rds_instance_id:
        storage = get_metric(
            namespace="AWS/RDS",
            metric_name="FreeStorageSpace",
            dimensions=[{"Name": "DBInstanceIdentifier", "Value": rds_instance_id}],
        )
    if storage is not None:
        storage_gb = round(storage / (1024 ** 3), 2)
        metrics.append({"metric_name": "rds_free_storage_gb", "metric_value": storage_gb, "unit": "GB"})

    # ALB 5XX Errors (Sum over the period)
    # ALB arn_suffix is needed — fetch it dynamically
    alb_arn_suffix = get_alb_arn_suffix()
    if alb_arn_suffix:
        errors_5xx = get_metric(
            namespace="AWS/ApplicationELB",
            metric_name="HTTPCode_ELB_5XX_Count",
            dimensions=[{"Name": "LoadBalancer", "Value": alb_arn_suffix}],
            stat="Sum",
        )
        metrics.append({
            "metric_name": "alb_5xx_errors",
            "metric_value": errors_5xx if errors_5xx is not None else 0,
            "unit": "count",
        })

        # ALB Request Count
        req_count = get_metric(
            namespace="AWS/ApplicationELB",
            metric_name="RequestCount",
            dimensions=[{"Name": "LoadBalancer", "Value": alb_arn_suffix}],
            stat="Sum",
        )
        metrics.append({
            "metric_name": "alb_request_count",
            "metric_value": req_count if req_count is not None else 0,
            "unit": "count",
        })

    return metrics


def get_rds_instance_id():
    """Look up the RDS instance identifier by project name tag."""
    rds = boto3.client("rds", region_name=AWS_REGION)
    try:
        paginator = rds.get_paginator("describe_db_instances")
        for page in paginator.paginate():
            for instance in page["DBInstances"]:
                tags = {t["Key"]: t["Value"] for t in instance.get("TagList", [])}
                if tags.get("Name", "") == f"{PROJECT_NAME}-rds-instance":
                    return instance["DBInstanceIdentifier"]
    except Exception as e:
        print(f"Warning: Could not find RDS instance: {e}")
    return None


def get_alb_arn_suffix():
    """Look up the ALB ARN suffix by project name tag."""
    elbv2 = boto3.client("elbv2", region_name=AWS_REGION)
    try:
        response = elbv2.describe_load_balancers()
        for lb in response["LoadBalancers"]:
            if PROJECT_NAME in lb.get("LoadBalancerName", ""):
                # arn_suffix is everything after "app/"
                arn = lb["LoadBalancerArn"]
                return arn.split(":loadbalancer/")[-1]
    except Exception as e:
        print(f"Warning: Could not find ALB: {e}")
    return None


def post_metrics(metrics):
    """POST each metric to the dashboard API."""
    success, failed = 0, 0
    for metric in metrics:
        try:
            resp = requests.post(METRICS_ENDPOINT, json=metric, timeout=10)
            if resp.status_code == 201:
                print(f"  OK  {metric['metric_name']} = {metric['metric_value']} {metric['unit']}")
                success += 1
            else:
                print(f"  FAIL {metric['metric_name']}: {resp.status_code} {resp.text}")
                failed += 1
        except requests.RequestException as e:
            print(f"  ERR  {metric['metric_name']}: {e}")
            failed += 1
    return success, failed


def main():
    print(f"Collecting CloudWatch metrics for {PROJECT_NAME}...")
    print(f"Target: {METRICS_ENDPOINT}\n")

    metrics = collect_all_metrics()

    if not metrics:
        print("No metrics collected. Check AWS credentials and resource names.")
        sys.exit(1)

    print(f"Collected {len(metrics)} metrics. Posting to dashboard...\n")
    success, failed = post_metrics(metrics)

    print(f"\nDone: {success} posted, {failed} failed.")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
