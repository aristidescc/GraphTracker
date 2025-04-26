from flask import Flask
from flask_cors import CORS
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to allow imports
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from backend.routes import register_routes
from backend.models import init_db

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Database configuration - Using SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///graph.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    init_db(app)
    
    # Register routes
    register_routes(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)
