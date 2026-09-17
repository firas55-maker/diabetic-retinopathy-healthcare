from flask import Flask
from config import config
from database import db, init_db
from models import User, Hospital, Patient, RoleEnum, SexEnum

def create_app(config_name='development'):
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize database
    db.init_app(app)

    with app.app_context():
        # Create all tables
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
