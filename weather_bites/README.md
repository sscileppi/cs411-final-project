# Web Application Project

This project is a Flask-based web application designed to simulate real-world software development scenarios. The application demonstrates proficiency in backend development, API integration, database management, and deployment via Docker.


## Features

- User account management with secure password storage.
- Integration with an external API (e.g., `random.org`) to fetch and manipulate data.
- Robust logging for application activity tracking.
- Comprehensive testing, including unit tests and smoke tests.
- Containerized using Docker for easy deployment.


## Application Routes

### Health Check
- **Route Name and Path**: `/health`
- **Request Type**: `GET`
- **Purpose**: Verifies that the application is running.
- **Response Format**: 
   ```
   { "status": "ok" }
   ```
---
# User Authentication
## Create Account
- **Route Name and Path**: /create-account
- **Request Type**: POST
- **Purpose**: Allows a new user to create an account.
- **Request Format**: 
   ```  
   {
      "username": "string",
      "password": "string"
   }
   ```
- **Response Format**: 
   ```
   { "message": "Account created successfully." }
   ```
## Login
- **Route Name and Path**: `/login`
- **Request Type**: `POST`
- **Purpose**: Verifies user credentials.
- **Request Format**:
   ```
   {
      "username": "string",
      "password": "string"
   }
   ```
## Update Password
- **Route Name and Path**: `/update-password`
- **Request Type**: `PUT`
- **Purpose**: Updates a user's password.
- **Request Format**: 
   ```
   {
      "username": "string",
      "old_password": "string",
      "new_password": "string"
   }
   ```
- **Response Format**: 
   ```
   { "message": "Password updated successfully." }
   ```
---
# API Integration
## Random Number Generator
- **Route Name and Path**: `/random-number`
- **Request Type**: `GET`
- **Purpose**: Fetches a random number from random.org.
- **Response Format:**: 
   ```
   { "random_number": 0.56 }
   ```
## Additional API Routes
- Implement additional API-based functionality as needed (e.g., storing data, returning statistics).
---
# Setup and Installation
## Prerequisites
- Python 3.9 or higher
- Docker (for containerized deployment)
---
# Installation
1. Clone the repository: 
   ```
   git clone https://github.com/your-repo/project-name.git
   cd project-name
   ```
2. Create a virtual environment and activate it:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up the .env file:
   - Copy the .env.template file and rename it to .env.
   - Update the environment variables (e.g., DB_PATH, API_KEYS).
5. Initialize the database:
   ```
   bash scripts/create_db.sh
   ```
6. Run the application:
   ```
   flask run
   ```
---
# Running Tests
To run the tests:
   '''
   pytest tests/
   '''
# Docker Deployment
1. Build the Docker image:
   ```
   docker build -t web-app-project .
   ```
2. Run the Docker container:
   ```
   docker run -d -p 5000:5000 --env-file .env web-app-project
   ```
---
# File Structure
   ```
   .
   ├── app/                  # Flask application code
   ├── tests/                # Unit tests
   ├── scripts/              # Scripts for database setup
   ├── Dockerfile            # Docker configuration
   ├── requirements.txt      # Python dependencies
   ├── .env.template         # Template for environment variables
   ├── README.md             # Project documentation
   ```
---
# Contributors
This project was developed by the team as part of a course assignment. Each member contributed equally to the project.
---
# License
This project is for educational purposes and does not include a specific license.