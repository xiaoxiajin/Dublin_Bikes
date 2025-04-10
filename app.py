from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from urllib.parse import unquote

import os
import threading
import mysql.connector
import json
import pickle
import pandas as pd
# import other functions
import website.login_routes
import website.stations_routes
import website.scraper_dublin_bike
import website.weather_routes
import website.database_connector

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'website', 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'website', 'static')


app = Flask(__name__, 
            template_folder=TEMPLATE_DIR, 
            static_folder=STATIC_DIR)
CORS(app)

# set secret key
app.secret_key = os.urandom(24)

# page
app.route('/')(website.login_routes.root)
app.route('/index.html')(website.login_routes.root)
app.route('/about.html')(website.login_routes.about)
app.route('/use.html')(website.login_routes.how_to_use)
app.route('/station.html')(website.login_routes.stations)
app.route('/contact.html')(website.login_routes.contact)

# login_routes
app.route('/login.html', methods=['GET', 'POST'])(website.login_routes.login)
app.route('/logout')(website.login_routes.logout)
app.route('/sign-up.html')(website.login_routes.sign_up)

# station_routes
app.route('/get_api_key')(website.stations_routes.get_api_key)
app.route('/stations')(website.stations_routes.get_stations)
app.route('/availability')(website.stations_routes.get_availability)
app.route('/update_bikes')(website.stations_routes.update_bikes)
app.route('/station_data')(website.stations_routes.get_station_data)

# weather_routes
app.route('/weather', methods=['GET', 'POST'])(website.weather_routes.get_weather)
app.route('/update_weather')(website.weather_routes.update_weather)


@app.route('/predict', methods=['GET'])
def predict():
    station_id = request.args.get('station_id')
    date_str = request.args.get('datetime')

    if not station_id or not date_str:
        return jsonify({'error': 'Missing station_id or datetime'}), 400

    try:
        model_path = f"machine_learning/station_models/station_{station_id}.pkl"
        if not os.path.exists(model_path):
            return jsonify({'error': 'Model not found'}), 404

        with open(model_path, 'rb') as f:
            model = pickle.load(f)

        clean_date_str = unquote(date_str)
        # clean_date_str = date_str.split('=')[1]
        dt = pd.to_datetime(clean_date_str)
        # print(date_str)
        input_df = pd.DataFrame({
            'num_docks_available': 10,
            'day': [dt.day],
            'hour': [dt.hour],
            'avg_air_temp': 10.0,
            'avg_humidity': 24.0,
            'day_name': [dt.dayofweek],
        })

        prediction = model.predict(input_df)
        print(prediction)
        # pred_30 = max(0, 1)
        # pred_60 = max(0, 2)

        return jsonify(prediction[0])

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/station_trend', methods=['GET'])
def get_station_trend():
    station_id = request.args.get('station_id')
    
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

            # 预测
            prediction = model.predict(input_df)
            trend_data.append({
                'time': f"{hour:02d}:00",
                'bike_count': int(max(0, prediction[0]))
            })

        return jsonify(trend_data)

    except Exception as e:
        # handle exception in getting trend
        import traceback
        print(f"Error in get_station_trend: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
    
# handle error
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# schedule
def schedule_task():
    website.stations_routes.schedule_bike_update()

def schedule_bike_update():
    # Start the scheduling logic in a background thread
    threading.Thread(target=schedule_task, daemon=True).start()


if __name__ == '__main__':
    website.scraper_dublin_bike.fetch_bike_stations()

    schedule_bike_update()
    
    # run at local:
    print("Flask API is running at http://127.0.0.1:5000/")
    app.run(host='127.0.0.1', port=5000, debug=True)

    # run at EC2:
    # app.run(host='0.0.0.0', port=5000, debug=True)