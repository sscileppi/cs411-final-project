from flask_sqlalchemy import SQLAlchemy

# Initialize the database
db = SQLAlchemy()

# Function to initialize the database schema
def init_db(app):
    db.init_app(app)
    from models.snack_location import SnackLocation
    db.create_all(app=app)  # Creates the tables
