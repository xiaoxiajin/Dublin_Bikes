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
app.route('/station_data', methods=['GET'])(website.stations_routes.get_station_data)
app.route('/station_prediction')(website.stations_routes.get_station_prediction)

# weather_routes
app.route('/weather', methods=['GET', 'POST'])(website.weather_routes.get_weather)
app.route('/update_weather')(website.weather_routes.update_weather)



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
    # print("Flask API is running at http://127.0.0.1:5000/")
    # app.run(host='127.0.0.1', port=5000, debug=True)

    # run at EC2:
    app.run(host='0.0.0.0', port=5000, debug=True)