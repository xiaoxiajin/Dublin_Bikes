import requests
import schedule
import time
from datetime import datetime, timedelta, timezone
from sqlalchemy import text

import sys
import os
from dotenv import load_dotenv
load_dotenv()

# Get the absolute path of the 'swe' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from flask import Flask, jsonify
import threading
from website.config import config 

lock = threading.Lock() # avoid task execute more than one times

# Create Flask application
app = Flask(__name__)

# latitude and longitude of Dublin
LAT = 53.3498  # latitude
LON = -6.2603  # longitude

schedule_started = False # global variable, avoiding dupulicated tasks scheduling

def query_weatherAPI():
    ''' Get weather data hourly and store into database.'''
    URL = "https://api.openweathermap.org/data/3.0/onecall"

    params = {
        "lat": LAT,
        "lon": LON,
        "appid": config.WEATHER_API,
        "exclude": "minutely,alerts",
        "units": "metric",  # temperature unit
        "lang": "en"  # language
    }

    # Make the API request
    response = requests.get(URL, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the weather data from the JSON response
        data = response.json()     

        # Extract `current` weather data
        current = data["current"]
        dt = datetime.fromtimestamp(current["dt"], tz=timezone.utc)
        insert_current_weather(
            dt,
            current["feels_like"],
            current["humidity"],
            current["pressure"],
            datetime.fromtimestamp(current["sunrise"], tz=timezone.utc),
            datetime.fromtimestamp(current["sunset"], tz=timezone.utc),
            current["temp"],
            current.get("uvi", 0.0),
            current["weather"][0]["id"],
            current["weather"][0]["main"],
            current["weather"][0]["description"],
            current["weather"][0]["icon"],
            current.get("wind_gust", 0.0),
            current["wind_speed"],
            current.get("rain", {}).get("1h", 0.0),
            current.get("snow", {}).get("1h", 0.0)
        )


        # Extract `hourly` weather data
        for hourly in data["hourly"]:
            insert_hourly_weather(
                dt,
                datetime.fromtimestamp(hourly["dt"], tz=timezone.utc),
                hourly["feels_like"],
                hourly["humidity"],
                hourly.get("pop", 0.0),
                hourly["pressure"],
                hourly["temp"],
                hourly.get("uvi", 0.0),
                hourly["weather"][0]["id"],
                hourly["wind_speed"],
                hourly.get("wind_gust", 0.0),
                hourly.get("rain", {}).get("1h", 0.0),
                hourly.get("snow", {}).get("1h", 0.0)
            )

        # Extract `daily` weather data
        for daily in data["daily"]:
            insert_daily_weather(
                dt,
                datetime.fromtimestamp(daily["dt"], tz=timezone.utc),
                daily["humidity"],
                daily.get("pop", 0.0),
                daily["pressure"],
                daily["temp"]["max"],
                daily["temp"]["min"],
                daily.get("uvi", 0.0),
                daily["weather"][0]["id"],
                daily["wind_speed"],
                daily.get("wind_gust", 0.0),
                daily.get("rain", 0.0),  # `rain` -> float
                daily.get("snow", 0.0)   # `snow` -> float
            )

            # print("Weather data updated successfully.")
       
    else:
        print(f"API Request Failed, status code: {response.status_code}")    
        print(response.text) 

def safe_query_weatherAPI():
    if lock.acquire(blocking=False):  # avoid many tasks execute simoutaneously
        try:
            query_weatherAPI()
        finally:
            lock.release()

def insert_current_weather(dt, feels_like, humidity, pressure, sunrise, sunset, temp, uvi,
                           weather_id, weather_main, weather_description, weather_icon,
                           wind_gust, wind_speed, rain_1h, snow_1h):
    sql_insert = text("""
        INSERT INTO current_weather (
            dt, feels_like, humidity, pressure, sunrise, sunset, temp, uvi,
            weather_id, weather_main, weather_description, weather_icon,
            wind_gust, wind_speed, rain_1h, snow_1h
        )
        VALUES (
            :dt, :feels_like, :humidity, :pressure, :sunrise, :sunset, :temp, :uvi,
            :weather_id, :weather_main, :weather_description, :weather_icon,
            :wind_gust, :wind_speed, :rain_1h, :snow_1h
        )
        ON DUPLICATE KEY UPDATE 
            feels_like = VALUES(feels_like),
            humidity = VALUES(humidity),
            pressure = VALUES(pressure),
            sunrise = VALUES(sunrise),
            sunset = VALUES(sunset),
            temp = VALUES(temp),
            uvi = VALUES(uvi),
            weather_id = VALUES(weather_id),
            weather_main = VALUES(weather_main),
            weather_description = VALUES(weather_description),
            weather_icon = VALUES(weather_icon),
            wind_gust = VALUES(wind_gust),
            wind_speed = VALUES(wind_speed),
            rain_1h = VALUES(rain_1h),
            snow_1h = VALUES(snow_1h);
    """)

    with config.engine.connect() as connection:
        connection.execute(sql_insert, locals())
        connection.commit()

def insert_hourly_weather(dt, future_dt, feels_like, humidity, pop, pressure, temp, uvi, weather_id, wind_speed, wind_gust, rain_1h, snow_1h):
    sql_insert = text("""
        INSERT INTO hourly_weather (dt, future_dt, feels_like, humidity, pop, pressure, temp, uvi, weather_id, wind_speed, wind_gust, rain_1h, snow_1h)
        VALUES (:dt, :future_dt, :feels_like, :humidity, :pop, :pressure, :temp, :uvi, :weather_id, :wind_speed, :wind_gust, :rain_1h, :snow_1h)
        ON DUPLICATE KEY UPDATE 
            feels_like = VALUES(feels_like),
            humidity = VALUES(humidity),
            pop = VALUES(pop),
            pressure = VALUES(pressure),
            temp = VALUES(temp),
            uvi = VALUES(uvi),
            weather_id = VALUES(weather_id),
            wind_speed = VALUES(wind_speed),
            wind_gust = VALUES(wind_gust),
            rain_1h = VALUES(rain_1h),
            snow_1h = VALUES(snow_1h);
    """)

    with config.engine.connect() as connection:
        connection.execute(sql_insert, locals())
        connection.commit()

def insert_daily_weather(dt, future_dt, humidity, pop, pressure, temp_max, temp_min, uvi, weather_id, wind_speed, wind_gust, rain, snow):
    sql_insert = text("""
        INSERT INTO daily_weather (dt, future_dt, humidity, pop, pressure, temp_max, temp_min, uvi, weather_id, wind_speed, wind_gust, rain, snow)
        VALUES (:dt, :future_dt, :humidity, :pop, :pressure, :temp_max, :temp_min, :uvi, :weather_id, :wind_speed, :wind_gust, :rain, :snow)
        ON DUPLICATE KEY UPDATE 
            humidity = VALUES(humidity),
            pop = VALUES(pop),
            pressure = VALUES(pressure),
            temp_max = VALUES(temp_max),
            temp_min = VALUES(temp_min),
            uvi = VALUES(uvi),
            weather_id = VALUES(weather_id),
            wind_speed = VALUES(wind_speed),
            wind_gust = VALUES(wind_gust),
            rain = VALUES(rain),
            snow = VALUES(snow);
    """)

    with config.engine.connect() as connection:
        connection.execute(sql_insert, locals())
        connection.commit()

# Get recent weather data from database
def get_current_weather_from_db():
    with config.engine.connect() as connection:
        result = connection.execute(text("""
            SELECT dt, temp, feels_like, humidity, pressure, 
                   wind_speed, wind_gust, uvi, rain_1h, snow_1h,
                   sunrise, sunset, weather_id,
                   weather_main, weather_description, weather_icon
            FROM current_weather
            ORDER BY dt DESC
            LIMIT 1;
        """))
        weather_data = [dict(row._mapping) for row in result]

    if weather_data:
        # convert timedelta field into String
        for key, value in weather_data[0].items():
            if isinstance(value, timedelta):
                weather_data[0][key] = str(value)  
        return jsonify(weather_data[0])
    else:
        return jsonify({"message": "No weather data available"}), 404

# update weather data manually
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
