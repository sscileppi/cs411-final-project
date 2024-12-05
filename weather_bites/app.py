from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os

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
        temp (float): The current temperature in Celsius.

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
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric" 
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

#save snack
@app.route('/save-snack-location', methods=['POST'])
def save_snack_location():
    """
    Save a snack location to the user's favorites.

    Request JSON Body:
        location (str): The name of the snack location.
        user_id (int): The user's ID.

    Returns:
        JSON: Success message or error message.
    """
    data = request.json
    location = data.get('location')
    user_id = data.get('user_id')

    if not location or not user_id:
        return jsonify({'error': 'Location and user ID are required'}), 400

    new_snack_location = SnackLocation(name=location, user_id=user_id)
    db.session.add(new_snack_location)
    db.session.commit()

    return jsonify({'message': f'Snack location "{location}" saved successfully!'}), 201

#rate snack
@app.route('/rate-snack-location', methods=['POST'])
def rate_snack_location():
    """
    Rate a saved snack location.

    Request JSON Body:
        location (str): The name of the snack location.
        user_id (int): The user's ID.
        rating (int): The user's rating (1-5).

    Returns:
        JSON: Success message or error message.
    """
    data = request.json
    location = data.get('location')
    user_id = data.get('user_id')
    rating = data.get('rating')

    if not location or not user_id or not rating:
        return jsonify({'error': 'Location, user ID, and rating are required'}), 400

    snack = SnackLocation.query.filter_by(name=location, user_id=user_id).first()
    if not snack:
        return jsonify({'error': 'Snack location not found'}), 404

    snack.rating = rating
    db.session.commit()

    return jsonify({'message': f'Rated "{location}" with {rating} stars!'}), 200

#write review

#viewing favorite snack location
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)