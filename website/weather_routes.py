from flask import jsonify
import requests


# import existing functions
from website.scraper_weather import get_current_weather_from_db, safe_query_weatherAPI
from website.config import config 

import os

def get_weather():
    '''
    Fetch current weather data from OpenWeatherMap API for Dublin.
    
    Key Features:
    - Uses direct API call to get current weather
    - Retrieves weather for specific coordinates (Dublin)
    - Converts temperature to metric units
    
    API Parameters:
    - Latitude: 53.2059
    - Longitude: -6.1537
    - Units: Metric
    
    Returns:
        JSON response containing current weather information

    '''
    response = requests.get("https://api.openweathermap.org/data/2.5/weather", params={"lat": 53.2059, "lon": -6.1537, "appid": os.getenv("Weather_Api"), "units": "metric"})
    return jsonify(response.json())

def update_weather():
    '''
    Manually trigger a comprehensive weather data update.
    
    Key Operations:
    - Calls safe_query_weatherAPI() to fetch and store detailed weather data
    - Provides a way to manually refresh weather information
    
    Returns:
        JSON response confirming successful data update
    
    Note:
    - Uses a thread-safe method to query weather API
    - Stores data in database instead of just fetching current weather

    '''
    safe_query_weatherAPI()
    return jsonify({"message": "Weather data updated successfully!"})
