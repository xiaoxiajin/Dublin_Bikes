import sys
import os
# Get the absolute path of the 'swe' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
import traceback
from datetime import datetime, timezone
from sqlalchemy import text
# from urllib.parse import quote_plus
from website.config import config 
# from dotenv import load_dotenv
# load_dotenv()

# Load env information
# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))
# DB_HOST = "localhost"
# DB_PORT = os.getenv("DB_PORT")
# DB_NAME = "dublin_cycle"
# JCKEY = os.getenv("JCKEY")
# NAME = os.getenv("NAME")
# STATIONS_URL = os.getenv("STATIONS_URL")
# engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def fetch_bike_stations():
    '''Fetch bike station occupancy information'''
    try:
        response = requests.get(config.STATIONS_URL, params={"apiKey": config.JCKEY, "contract": config.NAME})  
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
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n Dublin bike data updated. {timestamp}\n")

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

    with config.engine.connect() as connection:
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
    try:
        with config.engine.connect() as connection:
            for station in stations:
                # add secure timestamp
                last_update = station.get('last_update')
                
                # if last_update exists
                if last_update is not None:
                    try:
                        timestamp = datetime.fromtimestamp(float(last_update) / 1000, tz=timezone.utc)
                    except (TypeError, ValueError) as e:
                        print(f"Error processing timestamp for station {station.get('number')}: {e}")
                        timestamp = datetime.now(timezone.utc)
                else:
                    # use current time for timestamp
                    timestamp = datetime.now(timezone.utc)
                
                # insert availability data
                availability_query = text("""
                    INSERT INTO availability 
                    (number, available_bikes, available_bike_stands, last_update, status) 
                    VALUES (:number, :available_bikes, :available_bike_stands, :last_update, :status)
                    ON DUPLICATE KEY UPDATE 
                    available_bikes = :available_bikes,
                    available_bike_stands = :available_bike_stands,
                    last_update = :last_update,
                    status = :status
                """)
                
                connection.execute(availability_query, {
                    
                    "number": station["number"],
                    "last_update": timestamp,
                    "available_bikes": station["available_bikes"],
                    "available_bike_stands": station["available_bike_stands"],
                    "status": station["status"]
                })
            
            connection.commit()
    
    except Exception as e:
        print(f"Error inserting availability data: {e}")
        

