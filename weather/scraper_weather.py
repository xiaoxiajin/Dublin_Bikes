import requests
from datetime import datetime

import sys
import os
# Get the absolute path of the 'swe' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import dbinfo

# OpenWeather API Key
API_KEY = dbinfo.Weather_Api

# latitude and longitude of Dublin
LAT = 53.3498  # latitude
LON = -6.2603  # longitude

today = datetime.today().strftime("%Y/%m/%d")
curr_time = datetime.now().strftime("%H:%M:%S")

def query_weatherAPI():

    URL = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "lat": LAT,
        "lon": LON,
        "appid": API_KEY,
        "units": "metric",  # temperature unit
        "lang": "en"  # language
    }

    # Make the API request
    response = requests.get(URL, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the weather data from the JSON response
        data = response.json()

        weather_desc = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        wind_deg = data["wind"]["deg"]

        print("City: Dublin")
        print(f"Weather: {weather_desc}")
        print(f"Temperature: {temperature}°C")
        print(f"Humidity: {humidity}%")
        print(f"Wind Speed: {wind_speed} m/s, Wind Deg: {wind_deg}°")

    else:
        print("Error:", response.status_code)    

query_weatherAPI()