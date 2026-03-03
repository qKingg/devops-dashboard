from flask import Flask
from .config import Config
from .models import db
from .routes import api
from sqlalchemy import inspect

def create_app():
    """
    Application factory pattern.
    Creates and configures a new Flask instance each time it's called.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database with this app
    db.init_app(app)

    # Make config accessible in routes via blueprint
    api.config = app.config

    # Register the routes blueprint
    app.register_blueprint(api)

    # Create tables if they don't exist
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table("metrics"):
            db.create_all()

    return app