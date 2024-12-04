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
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY") #add in our api key

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
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric" #put our api key
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