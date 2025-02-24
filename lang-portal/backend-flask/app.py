import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from routes import api  # Ensure this is correct
from models import db  # Correct import of SQLAlchemy instance

def create_app():
    # Initialize Flask app
    app = Flask(__name__)

    # Enable CORS for API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Configure SQLite database
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'instance', 'words.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy with app
    db.init_app(app)

    # Register API routes
    app.register_blueprint(api)

    # Ensure the database is created
    with app.app_context():
        db.create_all()  # This creates tables in the SQLite database

    # Define base route
    @app.route('/')
    def home():
        return "Welcome to the Language Portal API!"

    return app

# Entry point
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)