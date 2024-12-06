from flask_sqlalchemy import SQLAlchemy

# Initialize the database
db = SQLAlchemy()

# Function to initialize the database schema
def init_db(app):
    db.init_app(app)
    from models.review import Review
    db.create_all(app=app)  # Creates the tables
