from flask import jsonify
import requests


# import existing functions
from website.scraper_weather import get_current_weather_from_db, safe_query_weatherAPI
from website.config import config 

import os

# get current weather data
def get_weather():
    response = requests.get("https://api.openweathermap.org/data/2.5/weather", params={"lat": 53.2059, "lon": -6.1537, "appid": os.getenv("Weather_Api"), "units": "metric"})
    return jsonify(response.json())

# update weather data manually
def update_weather():
    safe_query_weatherAPI()
    return jsonify({"message": "Weather data updated successfully!"})
