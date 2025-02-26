import requests
import schedule
import time
from datetime import datetime
from datetime import timedelta
from sqlalchemy import create_engine, text

import sys
import os

# Get the absolute path of the 'swe' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import dbinfo

from flask import Flask, jsonify
import threading

lock = threading.Lock() # avoid task execute more than one times

# Create Flask application
app = Flask(__name__)

# OpenWeather API Key
API_KEY = dbinfo.Weather_Api

# Database connection details:
DB_NAME = "dublin_cycle"
engine = create_engine(f"mysql+pymysql://{dbinfo.DB_USER}:{dbinfo.DB_PASSWORD}@{dbinfo.DB_HOST}:{dbinfo.DB_PORT}/{DB_NAME}")

# latitude and longitude of Dublin
LAT = 53.3498  # latitude
LON = -6.2603  # longitude

schedule_started = False # global variable, avoiding dupulicated tasks scheduling

def query_weatherAPI():
    ''' Get weather data hourly and store into database.'''
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

        today = datetime.today().strftime("%Y/%m/%d")
        curr_time = datetime.now().strftime("%H:%M:%S")     

        # Show data
        # print("City: Dublin")
        # print(f"Weather: {weather_desc}")
        # print(f"Temperature: {temperature}°C")
        # print(f"Humidity: {humidity}%")
        # print(f"Wind Speed: {wind_speed} m/s, Wind Deg: {wind_deg}°")
        print(f"✅ {curr_time} - Get weather data successfully: {weather_desc}, {temperature}°C, humidity: {humidity}%")

        # Insert data into RDS
        insert_weather_data(today, curr_time, weather_desc, temperature, humidity, wind_speed, wind_deg)

        # sql_query = text("DESC historical_weather;")
        # with engine.connect() as connection:
        #     connection.execute(sql_query)
        #     connection.commit()

    else:
        print(f"API Request Failed, status code: {response.status_code}")    
        print(response.text) 

def safe_query_weatherAPI():
    if lock.acquire(blocking=False):  # avoid many tasks execute simoutaneously
        try:
            query_weatherAPI()
        finally:
            lock.release()

def insert_weather_data(date, time, weather, temp, humidity, wind_speed, wind_deg):
    # TODO: modify formulation
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

# Get recent weather data from database
@app.route('/weather', methods=['GET'])
def get_weather():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT date, TIME_FORMAT(time, '%H:%i:%s') AS time, weather, temp, humidity, wind_speed, wind_deg FROM historical_weather ORDER BY date DESC, time DESC LIMIT 1;"))
        weather_data = [dict(row._mapping) for row in result]

    if weather_data:
        # convert timedelta field into String
        for key, value in weather_data[0].items():
            if isinstance(value, timedelta):
                weather_data[0][key] = str(value)  
        return jsonify(weather_data[0])
    else:
        return jsonify({"message": "No weather data available"}), 404

# update weather data manually**
@app.route('/update_weather', methods=['GET'])
def update_weather():
    safe_query_weatherAPI()
    return jsonify({"message": "Weather data updated successfully!"})

def schedule_task():
    global schedule_started
    if schedule_started:  # If task has been registered, return directly
        return
    schedule_started = True

    schedule.clear()
    # Use schedule to let program execute hourly.
    schedule.every(1).hours.do(safe_query_weatherAPI)
    # for test:
    # schedule.every(10).seconds.do(safe_query_weatherAPI)
    while True:
        schedule.run_pending()
        time.sleep(60)
        # for test:
        # time.sleep(1)  # check it every 1 secs

if __name__ == '__main__':
    # Move schedule to a separate background thread so that it does not block the Flask server, allowing the API to remain responsive.
    threading.Thread(target=schedule_task, daemon=True).start()

    print("🚀 Flask API is running at http://127.0.0.1:5000/")
    app.run(host='127.0.0.1', port=5000, debug=False) 
    # debug=True may start two Flask instances, causing schedule_task() to run twice.
    # With debug turned off, only one process will be running, avoiding duplicate task scheduling.
