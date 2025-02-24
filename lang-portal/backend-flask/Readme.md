# Create and active environment

cd lang-portal/backend-flask

python3 -m venv venv

source venv/bin/activate

# Install Dependencies

pip install -r requirements.txt

# Run the Backend

python3 app.py

# initialize the database

python init_db.py