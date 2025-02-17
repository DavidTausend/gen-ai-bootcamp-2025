import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Import CORS correctly
from routes import api  # Ensure this is correct
from models import db  # Ensure this is correct

app = Flask(__name__)

# Enable CORS before registering routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'words.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Register API routes
app.register_blueprint(api)

# Ensure the database is created
with app.app_context():
    db.create_all()  # This creates the tables in SQLite

@app.route('/')
def home():
    return "Welcome to the Language Portal API!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Ensure it runs on all interfaces
