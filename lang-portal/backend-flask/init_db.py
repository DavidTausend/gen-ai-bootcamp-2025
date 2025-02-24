from app import create_app, init_db

# Create Flask app instance
app = create_app()

# Initialize the database within app context
with app.app_context():
    try:
        db_path = app.config['DATABASE']
        init_db(db_path)
        print(f"Database initialized successfully at: {db_path}")
    except Exception as e:
        print(f"Error initializing database: {e}")