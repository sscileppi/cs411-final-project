from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os
from weather_bites.weather_bites.models.snack_location import SnackLocation
from weather_bites.weather_bites.models.db import db

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)

# Predefined temperature ranges and snack locations
TEMPERATURE_LOCATIONS = {
    "<30": ["1369 Coffee House (hot chocolate)", "Soup Shack"],
    "31-45": ["1369 Coffee House", "Tatte"],
    "46-60": ["Blank Street Coffee", "Pavement Coffeehouse"],
    "61-75": ["Boba Tea and Snow Ice House", "Tiger Sugar"],
    "76-85": ["Levain", "Fomu"],
    ">85": ["JP Licks", "Kyo Matcha"]
}

# Weather API key
WEATHER_API_KEY = os.getenv("e466bb4e7cf0fb8cd7b3dcf74a1bea58") #add in our api key

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
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'error': 'Invalid username or password'}), 401


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

@app.route('/favorite-snack-location', methods=['POST'])
def favorite_snack_location():
    """
    Allows a user to mark a snack location as a favorite.
    
    Request JSON Body:
        user_id (int): The user ID of the customer.
        snack_location_id (int): The ID of the snack location.
    
    Returns:
        JSON: A success message if the snack location is favorited, or an error message.
    """
    data = request.json
    user_id = data.get('user_id')
    snack_location_id = data.get('snack_location_id')

    # Validate input
    if not user_id or not snack_location_id:
        return jsonify({"error": "user_id and snack_location_id are required"}), 400
    
    # Fetch snack location from the database
    snack_location = SnackLocation.query.get(snack_location_id)
    if not snack_location:
        return jsonify({"error": "Snack location not found"}), 404

    # Mark the snack location as a favorite (this example assumes a favorite flag on the SnackLocation)
    snack_location.favorite = True
    db.session.commit()

    return jsonify({"message": "Snack location marked as favorite"}), 200

@app.route('/rate-snack-location', methods=['POST'])
def rate_snack_location():
    """
    Allows a user to rate a snack location.

    Request JSON Body:
        snack_location_id (int): The ID of the snack location to rate.
        rating (int): The rating value (1-5).

    Returns:
        JSON: A success message if the rating is saved successfully, or an error message.
    """
    data = request.json
    snack_location_id = data.get('snack_location_id')
    rating = data.get('rating')

    # Validate input
    if not snack_location_id or not rating:
        return jsonify({"error": "snack_location_id and rating are required"}), 400
    
    # Check if rating is valid (e.g., 1-5)
    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    # Get the snack location from the database
    snack_location = db.session.query(SnackLocation).filter_by(id=snack_location_id).first()
    if not snack_location:
        return jsonify({"error": "Snack location not found"}), 404

    # Update the rating
    snack_location.rating = rating
    db.session.commit()

    return jsonify({"message": "Rating added successfully"}), 201

@app.route('/write-review', methods=['POST'])
def write_review():
    """
    Allows a user to write a review for a snack location.

    Request JSON Body:
        snack_location_id (int): The ID of the snack location to review.
        review (str): The review text.

    Returns:
        JSON: A success message if the review is saved successfully, or an error message.
    """
    data = request.json
    snack_location_id = data.get('snack_location_id')
    review = data.get('review')

    # Validate input
    if not snack_location_id or not review:
        return jsonify({"error": "snack_location_id and review are required"}), 400

    # Get the snack location from the database
    snack_location = db.session.query(SnackLocation).filter_by(id=snack_location_id).first()
    if not snack_location:
        return jsonify({"error": "Snack location not found"}), 404

    # Update the review
    snack_location.review = review
    db.session.commit()

    return jsonify({"message": "Review added successfully"}), 201


@app.route('/get-favorite-snack-locations', methods=['GET'])
def get_favorite_snack_locations():
    """
    Retrieves all snack locations marked as favorites.

    Returns:
        JSON: A list of favorite snack locations.
    """
    favorite_locations = db.session.query(SnackLocation).filter_by(favorite=True).all()

    # Convert the result to a list of dictionaries
    favorite_locations_dict = [location.to_dict() for location in favorite_locations]

    return jsonify(favorite_locations_dict), 200



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)