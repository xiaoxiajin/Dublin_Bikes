# start

import sys
import os
# Get the absolute path of the 'swe' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import dbinfo

# offer google map api
from flask import Flask, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app) # allow front end visit flask server

@app.route('/get_api_key')
def get_api_key():
    return jsonify({"api_key": dbinfo.GOOGLE_MAPS_API_KEY})

if __name__ == '__main__':
    app.run(debug=True, port=5000)




