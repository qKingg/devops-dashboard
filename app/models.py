from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class Metric(db.Model):
    """
    Stores time-series data points like CPU usage, memory, request counts.
    Each row is one measurement at one point in time.
    """
    __tablename__ = "metrics"

    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(100), nullable=False, index=True)
    metric_value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default="")  # "%", "MB", "count", etc.
    timestamp = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    def to_dict(self):
        """Convert to JSON-friendly dict for API responses."""
        return {
            "id": self.id,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat()
        }


class HealthCheck(db.Model):
    """
    Stores results of service health checks.
    Useful for tracking uptime and response times over time.
    """
    __tablename__ = "health_checks"

    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False)  # "healthy" or "unhealthy"
    response_time_ms = db.Column(db.Integer)
    details = db.Column(db.Text, default="")
    checked_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "service_name": self.service_name,
            "status": self.status,
            "response_time_ms": self.response_time_ms,
            "details": self.details,
            "checked_at": self.checked_at.isoformat()
        }