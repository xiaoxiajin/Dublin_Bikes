from flask import Flask, jsonify
import json
import os
import sys

app = Flask(__name__)
# Get the path of the 'weather' directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/stations', methods=['GET'])
def get_stations():
    # Get the path of the 'dublin_stations.json' file
    json_path = os.path.join(BASE_DIR, "..",'dublin_stations.json')
    
    with open(json_path, 'r') as file:
        stations = json.load(file)
    return jsonify(stations)

@app.route('/')
def root():
    return 'Navigate http://127.0.0.1:5000/stations'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000,debug=True)