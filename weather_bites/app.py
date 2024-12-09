from flask import Flask, request, jsonify
import requests
import random
from dotenv import load_dotenv
import os
from weather_bites.models.review import Review
from weather_bites.models.db import db, User, Favorite
import logging
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather_bites.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Initialize the database tables
initialized = False

@app.before_request
def initialize_database():
    global initialized
    if not initialized:
        with app.app_context():
            db.create_all()
        initialized = True

# Logging setup
logging.basicConfig(level=logging.INFO)

# Predefined temperature ranges and snack locations
TEMPERATURE_LOCATIONS = {
    "<30": ["1369 Coffee House", "Soup Shack"],
    "31-45": ["1369 Coffee House", "Tatte"],
    "46-60": ["Blank Street Coffee", "Pavement Coffeehouse"],
    "61-75": ["Boba Tea and Snow Ice House", "Tiger Sugar"],
    "76-85": ["Levain", "Fomu"],
    ">85": ["JP Licks", "Kyo Matcha"]
}
TEMPERATURE_SNACKS = {
    "<30": ["hot chocolate", "soup"],
    "31-45": ["chocolate croissant", "hot coffee"],
    "46-60": ["almond croissant", "everything cream cheese bagel"],
    "61-75": ["brown sugar bubble tea", "strawberry milk tea"],
    "76-85": ["chocolate-chip cookie", "ice cream cookie sandwich"],
    ">85": ["Cookies 'n' Cream Sundae", "Strawberry Matcha Latte"]
}
TEMPERATURE_SEASONAL= {
    "<30": ["peppermint hot chocolate"],
    "31-45": ["peppermint tea"],
    "46-60": ["apple cider donuts"],
    "61-75": ["acai bowl"],
    "76-85": ["lemonade"],
    ">85": ["frozen yogurt"]
}

# Weather API key
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check route to ensure the app is running.
    """
    logging.info("Health check called")
    return jsonify({"status": "healthy"}), 200

@app.route('/create-account', methods=['POST'])
def create_account():
    """
    Create a new user account.

    Request JSON Body:
        username (str): The desired username.
        password (str): The desired password.

    Returns:
        JSON: A success message if the account is created, or an error message.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    logging.info(f"User {username} created successfully")
    return jsonify({'message': 'Account created successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    """
    Log in a user by validating their password.

    Request JSON Body:
        username (str): The username.
        password (str): The password.

    Returns:
        JSON: A success message if the credentials are valid, or an error message.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        logging.info(f"User {username} logged in successfully")
        return jsonify({'message': 'Login successful'}), 200
    logging.warning(f"Failed login attempt for username: {username}")
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/update-password', methods=['PUT'])
def update_password():
    """
    Update a user's password.
    """
    data = request.json
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(old_password):
        user.set_password(new_password)
        db.session.commit()
        logging.info(f"Password updated for user {username}")
        return jsonify({'message': 'Password updated successfully'}), 200

    logging.warning(f"Failed password update for username: {username}")
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/add-favorite', methods=['POST'])
def add_favorite():
    """
    Add a favorite city for a user.
    """
    data = request.json
    username = data.get('username')
    city = data.get('city')

    user = User.query.filter_by(username=username).first()
    if not user:
        logging.warning(f"User {username} not found when adding favorite")
        return jsonify({'error': 'User not found'}), 404

    favorite = Favorite(user_id=user.id, city=city)
    db.session.add(favorite)
    db.session.commit()

    logging.info(f"Favorite city {city} added for user {username}")
    return jsonify({'message': f'City {city} added to favorites'}), 201


@app.route('/list-favorites', methods=['GET'])
def list_favorites():
    """
    List all favorite cities for a user.
    """
    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()

    if not user:
        logging.warning(f"User {username} not found when listing favorites")
        return jsonify({'error': 'User not found'}), 404

    favorites = Favorite.query.filter_by(user_id=user.id).all()
    favorite_cities = [f.city for f in favorites]

    logging.info(f"Favorites retrieved for user {username}")
    return jsonify({'favorites': favorite_cities}), 200

def get_locations_by_temperature(temp):
    """
    Determines snack locations based on the temperature range.

    Args:
        temp (float): The current temperature in Fahrenheit.

    Returns:
        list: A list of snack location names matching the temperature range.
    """
    if temp < 30:
        return TEMPERATURE_LOCATIONS["<30"]
    elif 31 <= temp <= 45:
        return TEMPERATURE_LOCATIONS["31-45"]
    elif 46 <= temp <= 60:
        return TEMPERATURE_LOCATIONS["46-60"]
    elif 61 <= temp <= 75:
        return TEMPERATURE_LOCATIONS["61-75"]
    elif 76 <= temp <= 85:
        return TEMPERATURE_LOCATIONS["76-85"]
    else:
        return TEMPERATURE_LOCATIONS[">85"]
    
def get_snacks_by_temperature(temp):
    """
    Determines snack  based on the temperature range.

    Args:
        temp (float): The current temperature in Fahrenheit.

    Returns:
        list: A list of snack location names matching the temperature range.
    """
    if temp < 30:
        return TEMPERATURE_SNACKS["<30"]
    elif 31 <= temp <= 45:
        return TEMPERATURE_SNACKS["31-45"]
    elif 46 <= temp <= 60:
        return TEMPERATURE_SNACKS["46-60"]
    elif 61 <= temp <= 75:
        return TEMPERATURE_SNACKS["61-75"]
    elif 76 <= temp <= 85:
        return TEMPERATURE_SNACKS["76-85"]
    else:
        return TEMPERATURE_SNACKS[">85"]
    
def get_seasonal_snacks_by_temperature(temp):
    """
    Determines snack  based on the temperature range.

    Args:
        temp (float): The current temperature in Fahrenheit.

    Returns:
        list: A list of snack location names matching the temperature range.
    """
    if temp < 30:
        return TEMPERATURE_SEASONAL["<30"]
    elif 31 <= temp <= 45:
        return TEMPERATURE_SEASONAL["31-45"]
    elif 46 <= temp <= 60:
        return TEMPERATURE_SEASONAL["46-60"]
    elif 61 <= temp <= 75:
        return TEMPERATURE_SEASONAL["61-75"]
    elif 76 <= temp <= 85:
        return TEMPERATURE_SEASONAL["76-85"]
    else:
        return TEMPERATURE_SEASONAL[">85"]
    
def fetch_weather(city):
    """
    Fetches the current temperature for a given city using the OpenWeatherMap API.

    Args:
        city (str): The name of the city.

    Returns:
        float: The current temperature in Celsius if successful, or None if the API call fails.
    """

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=imperial" #put our api key

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['main']['temp']  # Return the current temperature
    return None


# Routes
@app.route('/')
def home():
    """
    Default route for the root path.
    """
    return jsonify({"message": "Welcome to the Weather Bites API! Refer to the documentation for available routes."})

@app.route('/get-snack-location', methods=['GET'])
def get_snack_location():
    """
    Recommends snack locations based on the current weather.

    Query Parameters:
        city (str): The name of the city.

    Returns:
        JSON: A dictionary containing the temperature and recommended snack locations.
    """
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City is required"}), 400
    
    temperature = fetch_weather(city)
    if temperature is not None:
        locations = get_locations_by_temperature(temperature)
        return jsonify({
            "temperature": temperature,
            "locations": locations
        }), 200
    
    return jsonify({"error": "Could not fetch weather data"}), 500

@app.route('/get-snack-recommendation', methods=['GET'])
def get_snack_recommendation():
    """
    Recommends a snack based on the current weather.

    Query Parameters:
        city (str): The name of the city.

    Returns:
        JSON: A dictionary containing the temperature and recommended snack.
    """
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City is required"}), 400
    
    temperature = fetch_weather(city)
    if temperature is not None:
        snacks = get_snacks_by_temperature(temperature)
        return jsonify({
            "temperature": temperature,
            "snacks": snacks
        }), 200
    
    return jsonify({"error": "Could not fetch weather data"}), 500

@app.route('/view-current-weather', methods=['GET'])
def view_current_weather():
    """
    Displays the current weather for a given city.

    Query Parameters:
        city (str): The name of the city.

    Returns:
        JSON: The current temperature and weather condition.
    """
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City is required"}), 400
    
    temperature = fetch_weather(city)
    if temperature is not None:
        return jsonify({
            "city": city,
            "temperature": temperature
        }), 200
    
    return jsonify({"error": "Could not fetch weather data"}), 500

@app.route('/get-snack-recommendation', methods=['GET'])
def get_seasonal_snack_recommendation():
    """
    Recommends a seasonal snack based on the current weather.

    Query Parameters:
        city (str): The name of the city.

    Returns:
        JSON: A dictionary containing the temperature and recommended snack.
    """
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City is required"}), 400
    
    temperature = fetch_weather(city)
    if temperature is not None:
        seasonal_snacks = get_seasonal_snacks_by_temperature(temperature)
        return jsonify({
            "temperature": temperature,
            "snacks": seasonal_snacks
        }), 200
    
    return jsonify({"error": "Could not fetch weather data"}), 500


@app.route('/get-snack-pairing', methods=['GET'])
def get_snack_pairing():
    """
    Recommends a snack pairing based on the current weather.

    Query Parameters:
        city (str): The name of the city.

    Returns:
        JSON: A dictionary containing the temperature, recommended snack, and drink.
    """
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City is required"}), 400
    
    temperature = fetch_weather(city)
    if temperature is not None:
        # Fetching both snack and seasonal snack pairings
        snacks = get_snacks_by_temperature(temperature)
        seasonal_snacks = get_seasonal_snacks_by_temperature(temperature)

        # Assuming pairing snack from both regular and seasonal snacks
        snack = random.choice(snacks)  # Choose a random snack
        seasonal_snack = seasonal_snacks[0]  # Choose the first seasonal snack 

        return jsonify({
            "temperature": temperature,
            "snack": snack,
            "drink": seasonal_snack
        }), 200
    
    return jsonify({"error": "Could not fetch weather data"}), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)