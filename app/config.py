import os


class Config:
    
    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "local-dev-key-change-in-prod")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # Database connection
    # Format: postgresql://user:password@host:port/dbname
    DB_USER = os.getenv("DB_USER", "dashboard")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "localpassword")
    DB_HOST = os.getenv("DB_HOST", "db")  # "db" = docker-compose service name
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "dashboard")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Disable SQLAlchemy event tracking (saves memory, we don't need it)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # App settings
    APP_NAME = os.getenv("APP_NAME", "DevOps Dashboard")
    APP_VERSION = os.getenv("APP_VERSION", "0.1.0")