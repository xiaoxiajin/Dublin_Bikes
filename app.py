# start

import sys
import os
# Get the absolute path of the 'swe' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import dbinfo


from flask import Flask, jsonify
from flask_cors import CORS
import threading
import time
import schedule

from bike_station_data.scraper_dublin_bike import fetch_bike_stations  # import fetch_bike_stations
from sqlalchemy import create_engine, text

# offer google map api
app = Flask(__name__)
CORS(app) # allow front end visit flask server

DB_NAME = "dublin_cycle"
engine = create_engine(f"mysql+pymysql://{dbinfo.DB_USER}:{dbinfo.DB_PASSWORD}@{dbinfo.DB_HOST}:{dbinfo.DB_PORT}/{DB_NAME}")

@app.route('/get_api_key')
def get_api_key():
    return jsonify({"api_key": dbinfo.GOOGLE_MAPS_API_KEY})

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)


@app.route('/stations', methods=['GET'])
def get_stations():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM station;"))
        stations = [dict(row._mapping) for row in result]
    return jsonify(stations)

@app.route('/availability', methods=['GET'])
def get_availability():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM availability ORDER BY last_update DESC;"))
        availability_data = [dict(row._mapping) for row in result]
    return jsonify(availability_data)

@app.route('/update_bikes', methods=['GET'])
def update_bikes():
    fetch_bike_stations()
    return jsonify({"message": "Bike station data updated successfully!"})

@app.route('/')
def root():
    return 'Navigate to http://127.0.0.1:5000/stations or http://127.0.0.1:5000/update_bikes'

def schedule_task():
    schedule.every(1).hours.do(fetch_bike_stations)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    threading.Thread(target=schedule_task, daemon=True).start()
    print("🚀 Flask API is running at http://127.0.0.1:5000/")
    app.run(host='127.0.0.1', port=5000, debug=True)




