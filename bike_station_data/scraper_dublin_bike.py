import sys
import os
# Get the absolute path of the 'swe' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dbinfo
import requests
import json
import time
import traceback

def fetch_bike_stations():
    while True:  # Keep the scraper running indefinitely
        try:
            print("\n🚲 Fetching Dublin Bikes Data...\n")
            response = requests.get(dbinfo.STATIONS_URL, params={"apiKey": dbinfo.JCKEY, "contract": dbinfo.NAME})  
            response.raise_for_status()  # Raise an exception for failed requests

            # Parse JSON response
            stations = response.json()

            # TODO: GET AVAILABILITY

            # Print details of the first 5 stations
            for station in stations[:5]:  
                print(f"📍 Station: {station['name']}")
                print(f"🔄 Status: {station['status']}")
                print(f"📍 Address: {station['address']}")
                print(f"🚲 Available Bikes: {station['available_bikes']}")
                print(f"🅿️ Available Stands: {station['available_bike_stands']}")
                print("-" * 40)

            # Save data to a JSON file
            with open("dublin_bikes.json", "w") as file:
                json.dump(stations, file, indent=4)

            print("\n✅ Data saved to 'dublin_bikes.json'.\n")

            # Sleep for 5 minutes before the next request
            time.sleep(5 * 60)

        except requests.exceptions.RequestException as e:
            print(f"\n❌ API Request Failed: {e}")
            print(traceback.format_exc())  # Print detailed error message

        except Exception as e:
            print(f"\n⚠️ Unexpected Error: {e}")
            print(traceback.format_exc())  # Print detailed traceback for debugging

# Run the scraper
fetch_bike_stations()
