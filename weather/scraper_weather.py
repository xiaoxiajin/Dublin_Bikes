import requests
from datetime import datetime
from sqlalchemy import create_engine, text

import sys
import os
# Get the absolute path of the 'swe' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import dbinfo

# OpenWeather API Key
API_KEY = dbinfo.Weather_Api

# Database connection details:
DB_NAME = "dublin_cycle"
engine = create_engine(f"mysql+pymysql://{dbinfo.DB_USER}:{dbinfo.DB_PASSWORD}@{dbinfo.DB_HOST}:{dbinfo.DB_PORT}/{DB_NAME}")

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

        # Insert data into RDS
        insert_weather_data(today, curr_time, weather_desc, temperature, humidity, wind_speed, wind_deg)

        # sql_query = text("DESC historical_weather;")
        # with engine.connect() as connection:
        #     connection.execute(sql_query)
        #     connection.commit()

    else:
        print("Error:", response.status_code)    

def insert_weather_data(date, time, weather, temp, humidity, wind_speed, wind_deg):
    sql_insert = text("""
        INSERT INTO historical_weather (date, time, weather, temp, humidity, wind_speed, wind_deg)
        VALUES (:date, :time, :weather, :temp, :humidity, :wind_speed, :wind_deg)
        ON DUPLICATE KEY UPDATE 
            weather = VALUES(weather),
            temp = VALUES(temp),
            humidity = VALUES(humidity),
            wind_speed = VALUES(wind_speed),
            wind_deg = VALUES(wind_deg);
    """)

    with engine.connect() as connection:
        connection.execute(sql_insert, {
            "date": date,
            "time": time,
            "weather": weather,
            "temp": temp,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "wind_deg": wind_deg
        })
        connection.commit()

query_weatherAPI()