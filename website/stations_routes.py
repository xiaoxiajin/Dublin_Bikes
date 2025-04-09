from flask import jsonify
from sqlalchemy import create_engine, text
import schedule
import time
from website.scraper_dublin_bike import fetch_bike_stations
from website.config import config 

# from urllib.parse import quote_plus

# import os
# from dotenv import load_dotenv
# load_dotenv()

# # Load env information
# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))
# DB_HOST = "localhost"
# DB_PORT = os.getenv("DB_PORT")
# DB_NAME = "dublin_cycle"
# GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def get_api_key():
    return jsonify({"api_key": config.GOOGLE_MAPS_API_KEY})

def get_stations():
    with config.engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM station;"))
        stations = [dict(row._mapping) for row in result]
    return jsonify(stations)

def get_availability():
    with config.engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM availability ORDER BY last_update DESC;"))
        availability_data = [dict(row._mapping) for row in result]
    return jsonify(availability_data)


def get_station_data():
    """
    get station data for visulization
    """
    engine = config.engine

    with engine.connect() as connection:
        query = text("""
            SELECT 
                s.number, s.name, s.address, s.banking, s.bike_stands, 
                s.position_lat, s.position_lng,
                a.available_bikes, a.available_bike_stands, 
                a.status, a.last_update
            FROM station s
            JOIN availability a ON s.number = a.number
        """)
        
        result = connection.execute(query)
        data = [dict(row) for row in result]
    
    # convert datetime to isoformat
    for row in data:
        if 'last_update' in row and row['last_update'] is not None:
            row['last_update'] = row['last_update'].isoformat()
    
    return jsonify(data)

def update_bikes():
    fetch_bike_stations()
    return jsonify({"message": "Bike station data updated successfully!"})

def schedule_bike_update():
    
    schedule.every(1).hours.do(fetch_bike_stations)
    while True:
        schedule.run_pending()
        time.sleep(60)