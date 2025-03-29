from flask import jsonify
from sqlalchemy import create_engine, text
import dbinfo
import schedule
import time
from website.scraper_dublin_bike import fetch_bike_stations

# database
DB_NAME = "dublin_cycle"
engine = create_engine(f"mysql+pymysql://{dbinfo.DB_USER}:{dbinfo.DB_PASSWORD}@{dbinfo.DB_HOST}:{dbinfo.DB_PORT}/{DB_NAME}")

def get_api_key():
    return jsonify({"api_key": dbinfo.GOOGLE_MAPS_API_KEY})

def get_stations():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM station;"))
        stations = [dict(row._mapping) for row in result]
    return jsonify(stations)

def get_availability():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM availability ORDER BY last_update DESC;"))
        availability_data = [dict(row._mapping) for row in result]
    return jsonify(availability_data)

def update_bikes():
    fetch_bike_stations()
    return jsonify({"message": "Bike station data updated successfully!"})

def schedule_bike_update():
    schedule.every(1).hours.do(fetch_bike_stations)
    while True:
        schedule.run_pending()
        time.sleep(60)