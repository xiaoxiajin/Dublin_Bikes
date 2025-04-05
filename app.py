from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os
import threading
import mysql.connector
import json

# import other functions
import website.login_routes
import website.stations_routes


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

# Database connection function
def get_db_connection():
    # Replace with your actual database connection details
    connection = mysql.connector.connect(
        host='your_database_host',
        user='your_database_user',
        password='your_database_password',
        database='your_database_name'
    )
    return connection

@app.route("/station_data")
def station_data():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # this query fetches your SQL table content
    query = """
        SELECT 
            s.number, s.name, s.address, s.banking, s.bike_stands, 
            s.position_lat, s.position_lng,
            a.available_bikes, a.available_bike_stands, 
            a.status, a.last_update
        FROM stations s
        JOIN availability a ON s.number = a.number
    """
    
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    
    # Convert datetime objects to strings to make them JSON serializable
    for row in data:
        if 'last_update' in row and row['last_update'] is not None:
            row['last_update'] = row['last_update'].isoformat()
    
    return jsonify(data)

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
    schedule_bike_update()
    
    # run at local:
    # print("Flask API is running at http://127.0.0.1:5000/")
    # app.run(host='127.0.0.1', port=5000, debug=True)

    # run at EC2:
    app.run(host='0.0.0.0', port=5000, debug=True)