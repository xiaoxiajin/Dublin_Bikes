from flask import jsonify, request
from sqlalchemy import text
import schedule
import time
import pickle
import pandas as pd
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from website.scraper_dublin_bike import fetch_bike_stations
from website.config import config 

def get_api_key():
    '''Retrieve the Google Maps API key for client-side use.'''
    return jsonify({"api_key": config.GOOGLE_MAPS_API_KEY})

def get_stations():
    '''Retrieve all bike station static information from the database.'''
    with config.engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM station;"))
        stations = [dict(row._mapping) for row in result]
    return jsonify(stations)

def get_availability():
    '''Retrieve bike station availability data from the database.'''
    with config.engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM availability ORDER BY last_update DESC;"))
        availability_data = [dict(row._mapping) for row in result]
    return jsonify(availability_data)


def get_station_data():
    '''Retrieve comprehensive bike station data for visualization.

    Combines static station information with current availability:
    - Joins station and availability tables
    - Includes location, capacity, and current bike/stand counts
    
    Data Processing:
    - Converts datetime to ISO format for frontend compatibility
    
    Returns:
        JSON array of merged station and availability data

    '''
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
        
        result = connection.execute(query).mappings()
        data = [dict(row) for row in result]
    
    # convert datetime to isoformat
    for row in data:
        if 'last_update' in row and row['last_update'] is not None:
            row['last_update'] = row['last_update'].isoformat()
    
    return jsonify(data)



def get_station_prediction():  
    '''Generate bike availability predictions for a specific station.
    
    Key Features:
    - Uses pre-trained machine learning model for each station
    - Predicts bike availability for every 2 hours in a day
    - Handles model loading and prediction errors
    
    Parameters:
    - station_id: Identifier for the specific bike station
    
    Returns:
        JSON array of predicted bike counts for different times
    
    Error Handling:
    - Validates station_id
    - Checks for model existence
    - Handles prediction and loading exceptions
    '''  
    # Set a default station_id = 1
    station_id = request.args.get('station_id','1')
    
    
    if not station_id:
        return jsonify({'error': 'Missing station_id'}), 400

    try:
        # ensure station_id type
        station_id = int(station_id.split(':')[0]) 

        # every two hours
        trend_times = list(range(0, 24, 2))  

        # load model
        model_path = f"machine_learning/station_models/station_{station_id}.pkl"
        
        # check file exists
        if not os.path.exists(model_path):
            return jsonify({'error': f'Model for station {station_id} not found'}), 404

        with open(model_path, 'rb') as f:
            model = pickle.load(f)

        # predict for every 2 hours
        trend_data = []
        for hour in trend_times:
            dt = pd.Timestamp.now().replace(hour=hour, minute=0, second=0)

            input_df = pd.DataFrame({
                'num_docks_available': [10],  
                'day': [dt.day],
                'hour': [dt.hour],
                'avg_air_temp': [10.0],  
                'avg_humidity': [24.0],   
                'day_name': [dt.dayofweek],
            })

            # predict
            prediction = model.predict(input_df)
            trend_data.append({
                'time': f"{hour:02d}:00",
                'bike_count': int(max(0, prediction[0]))
            })

        return jsonify(trend_data)

    except Exception as e:
        # handle exception in getting trend
        import traceback
        print(f"Error in get_station_prediction: {e}")        
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
    
def update_bikes():
    '''Manually trigger an update of bike station data.'''
    fetch_bike_stations()
    return jsonify({"message": "Bike station data updated successfully!"})

def schedule_bike_update():
    '''Set up a scheduled task to periodically update bike station data.
    
    Scheduling Details:
    - Runs fetch_bike_stations() every hour
    - Uses an infinite loop with sleep to manage scheduling
    
    Note: This function runs continuously in a separate thread
    '''
    
    schedule.every(1).hours.do(fetch_bike_stations)
    while True:
        schedule.run_pending()
        time.sleep(60)