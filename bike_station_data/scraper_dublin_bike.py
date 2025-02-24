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
from sqlalchemy import create_engine, text
import schedule
import threading

# Create a flask application
app = Flask(__name__)

DB_NAME = "dublin_cycle"
engine = create_engine(f"mysql+pymysql://{dbinfo.DB_USER}:{dbinfo.DB_PASSWORD}@{dbinfo.DB_HOST}:{dbinfo.DB_PORT}/{DB_NAME}")

def fetch_bike_stations():
    # while True:  # Keep the scraper running indefinitely
    try:
        print("\n🚲 Fetching Dublin Bikes Data...\n")
        response = requests.get(dbinfo.STATIONS_URL, params={"apiKey": dbinfo.JCKEY, "contract": dbinfo.NAME})  
        response.raise_for_status()  # Raise an exception for failed requests

        # Parse JSON response
        if response.status_code == 200: 
            stations = response.json()
        else:
            print(f"API Request Failed, status code: {response.status_code}")
            print(response.text)  
            return  
        
        insert_bike_data(stations)
        print("\n Dublin bike data updated. \n")

        # Print details of the first 5 stations
        # for station in stations[:5]:  
        #     print(f"📍 Station: {station['name']}")
        #     print(f"🔄 Status: {station['status']}")
        #     print(f"📍 Address: {station['address']}")
        #     print(f"🚲 Available Bikes: {station['available_bikes']}")
        #     print(f"🅿️ Available Stands: {station['available_bike_stands']}")
        #     print("-" * 40)

        # Save data to a JSON file
        # with open("dublin_bikes.json", "w") as file:
        #     json.dump(stations, file, indent=4)        

        # Sleep for 5 minutes before the next request
        # time.sleep(5 * 60)

    except requests.exceptions.RequestException as e:
        print(f"\n API Request Failed: {e}")
        print(traceback.format_exc())  # Print detailed error message
        
def insert_bike_data(stations):
    sql_insert = text("""
        INSERT INTO bike_stations (number, name, address, position_lat, position_lng, banking, bike_stands, available_bikes, available_bike_stands, status, last_update)
        VALUES (:number, :name, :address, :position_lat, :position_lng, :banking, :bike_stands, :available_bikes, :available_bike_stands, :status, :last_update)
        ON DUPLICATE KEY UPDATE 
            available_bikes = VALUES(available_bikes),
            available_bike_stands = VALUES(available_bike_stands),
            status = VALUES(status),
            last_update = VALUES(last_update);
    """)

    with engine.connect() as connection:
        for station in stations:
            connection.execute(sql_insert, {
                "number": station["number"],
                "name": station["name"],
                "address": station["address"],
                "position_lat": station["position"]["lat"],
                "position_lng": station["position"]["lng"],
                "banking": station["banking"],
                "bike_stands": station["bike_stands"],
                "available_bikes": station["available_bikes"],
                "available_bike_stands": station["available_bike_stands"],
                "status": station["status"],
                "last_update": station["last_update"]
            })
        connection.commit()

# Flask API endpoint
@app.route('/stations', methods=['GET'])
def get_stations():
    """ Get all bake station data in the database """
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM bike_stations;"))
        stations = [dict(row._mapping) for row in result]
    return jsonify(stations)

@app.route('/update_bikes', methods=['GET'])
def update_bikes():
    """ update bike station data manually """
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

    print("🚀 Flask API is running at http://127.0.0.1:5000/")
    app.run(host='127.0.0.1', port=5000, debug=True)