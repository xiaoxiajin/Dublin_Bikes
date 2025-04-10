# website/weather_routes.py

from flask import jsonify
import requests
from sqlalchemy import create_engine, text
from datetime import timedelta

# import existing functions
from website.scraper_weather import get_current_weather_from_db, safe_query_weatherAPI
from website.config import config 

import os
# from dotenv import load_dotenv
# load_dotenv()

# # database connection
# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_PORT = os.getenv("DB_PORT", "3306")
# DB_NAME = "dublin_cycle"

# engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# get current weather data
def get_weather():
    response = requests.get("https://api.openweathermap.org/data/2.5/weather", params={"lat": 53.2059, "lon": -6.1537, "appid": os.getenv("Weather_Api"), "units": "metric"})
    return jsonify(response.json())

# update weather data manually
def update_weather():
    safe_query_weatherAPI()
    return jsonify({"message": "Weather data updated successfully!"})
