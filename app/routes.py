from flask import Blueprint, jsonify, request, render_template
from .models import db, Metric, HealthCheck
from datetime import datetime, timezone

api = Blueprint("api", __name__)


@api.route("/health")
def health():
    """
    Health check endpoint. ALB and ECS uses this to know if the container
    is alive and ready to serve traffic...
    Returns DB connectivity status so you can catch connection issues...
    """
    try:
        db.session.execute(db.text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return jsonify({
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "version": api.config.get("APP_VERSION", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200 if db_status == "healthy" else 503


@api.route("/")
def dashboard():
    """Render HTML template"""
    return render_template("dashboard.html")


@api.route("/api/metrics", methods=["POST"])
def create_metric():
    """
    Ingest a metric data point.
    Expects JSON: {"metric_name": "cpu_usage", "metric_value": 72.5, "unit": "%"}
    """
    data = request.get_json()

    if not data or "metric_name" not in data or "metric_value" not in data:
        return jsonify({"error": "metric_name and metric_value required"}), 400

    metric = Metric(
        metric_name=data["metric_name"],
        metric_value=data["metric_value"],
        unit=data.get("unit", "")
    )
    db.session.add(metric)
    db.session.commit()

    return jsonify(metric.to_dict()), 201


@api.route("/api/metrics", methods=["GET"])
def get_metrics():
    """
    Retrieve metrics with optional filtering.
    Query params:
      ?name=cpu_usage  — filter by metric name
      ?limit=100       — max results (default 100)
    """
    name = request.args.get("name")
    limit = request.args.get("limit", 100, type=int)

    query = Metric.query.order_by(Metric.timestamp.desc())

    if name:
        query = query.filter_by(metric_name=name)

    metrics = query.limit(limit).all()

    return jsonify([m.to_dict() for m in metrics])