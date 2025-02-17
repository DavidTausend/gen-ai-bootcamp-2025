from flask_sqlalchemy import SQLAlchemy
from app import db

def upgrade():
    # Create all tables
    db.create_all()

def downgrade():
    # Drop all tables
    db.drop_all()
