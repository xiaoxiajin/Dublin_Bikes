from flask import Flask, jsonify
import sys
import os
# Get the absolute path of the 'swe' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dbinfo
import requests
# import json
import time
import traceback
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
import schedule
import threading
from flask_cors import CORS

# Create a flask application
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

DB_NAME = "dublin_cycle"
engine = create_engine(f"mysql+pymysql://{dbinfo.DB_USER}:{dbinfo.DB_PASSWORD}@{dbinfo.DB_HOST}:{dbinfo.DB_PORT}/{DB_NAME}")

def fetch_bike_stations():
    # while True:  # Keep the scraper running indefinitely
    try:
        # print("\n🚲 Fetching Dublin Bikes Data...\n")
        response = requests.get(dbinfo.STATIONS_URL, params={"apiKey": dbinfo.JCKEY, "contract": dbinfo.NAME})  
        response.raise_for_status()  # Raise an exception for failed requests

        # Parse JSON response
        if response.status_code == 200: 
            stations = response.json()
        else:
            print(f"API Request Failed, status code: {response.status_code}")
            print(response.text)  
            return  
        
        insert_station_data(stations)
        insert_availability_data(stations)
        print("\n Dublin bike data updated. \n")

    except requests.exceptions.RequestException as e:
        print(f"\n API Request Failed: {e}")
        print(traceback.format_exc())  # Print detailed error message
        
def insert_station_data(stations):
    """ Insert or update station static information """
    sql_insert = text("""
        INSERT INTO station (number, name, address, position_lat, position_lng, banking, bike_stands)
        VALUES (:number, :name, :address, :position_lat, :position_lng, :banking, :bike_stands)
        ON DUPLICATE KEY UPDATE 
            name = VALUES(name),
            address = VALUES(address),
            position_lat = VALUES(position_lat),
            position_lng = VALUES(position_lng),
            banking = VALUES(banking),
            bike_stands = VALUES(bike_stands);
    """)

    with engine.connect() as connection:
        for station in stations:
            connection.execute(sql_insert, {
                "number": station["number"],
                "name": station["name"],
                "address": station.get("address", "Unknown"), # avoid unknown address
                "position_lat": station["position"]["lat"],
                "position_lng": station["position"]["lng"],
                "banking": int(station["banking"]),
                "bike_stands": station["bike_stands"]
            })
        connection.commit()

def insert_availability_data(stations):
    """ Insert or update bike station availability data """
    sql_insert = text("""
        INSERT INTO availability (number, last_update, available_bikes, available_bike_stands, status)
        VALUES (:number, :last_update, :available_bikes, :available_bike_stands, :status)
        ON DUPLICATE KEY UPDATE 
            available_bikes = VALUES(available_bikes),
            available_bike_stands = VALUES(available_bike_stands),
            status = VALUES(status);
    """)

    with engine.connect() as connection:
        for station in stations:
            # last_update = datetime.strptime(station["lastUpdate"], "%Y-%m-%dT%H:%M:%SZ")
            if "last_update" in station:  # check if last_update exists
                last_update = datetime.fromtimestamp(station["last_update"] / 1000, tz=timezone.utc)
            else:
                # print(f"⚠️ Warning: Station {station['number']} has no 'last_update' field.")
                continue  # skip this station

            connection.execute(sql_insert, {
                "number": station["number"],
                "last_update": last_update,
                "available_bikes": station["available_bikes"],
                "available_bike_stands": station["available_bike_stands"],
                "status": station["status"]
            })
        connection.commit()

# Flask API endpoint
@app.route('/get_api_key')
def get_api_key():
    return jsonify({"api_key": dbinfo.GOOGLE_MAPS_API_KEY})


@app.route('/stations', methods=['GET'])
def get_stations():
    """ Get all bike station data in the database """
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM station;"))
        stations = [dict(row._mapping) for row in result]
    return jsonify(stations)

@app.route('/availability', methods=['GET'])
def get_availability():
    """ Get latest bike availability data """
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT * FROM availability ORDER BY last_update DESC;
        """))
        availability_data = [dict(row._mapping) for row in result]
    return jsonify(availability_data)

@app.route('/update_bikes', methods=['GET'])
def update_bikes():
    """ Manually update bike station data """
    fetch_bike_stations()
    return jsonify({"message": "Bike station data updated successfully!"})

@app.route('/')
def root():
    return 'Navigate to http://127.0.0.1:5000/stations or http://127.0.0.1:5000/update_bikes'

def schedule_task():
    # Use schedule to let program execute hourly.
    schedule.every(1).hours.do(fetch_bike_stations)
    # for test:
    # schedule.every(5).seconds.do(fetch_bike_stations)

    while True:
        schedule.run_pending()
        time.sleep(60) # check it every 60 secs
        # for test:
        # time.sleep(1)  # check it every 1 secs

if __name__ == '__main__':
    threading.Thread(target=schedule_task, daemon=True).start()
    # fetch_bike_stations()

    print("🚀 Flask API is running at http://127.0.0.1:5000/")
    app.run(host='127.0.0.1', port=5000, debug=True)