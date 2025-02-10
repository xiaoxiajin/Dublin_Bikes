import requests
import json

# API Configuration
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key
CONTRACT_NAME = "Dublin"
URL = f"https://api.jcdecaux.com/vls/v1/stations?contract={CONTRACT_NAME}&apiKey=20886f1d63eb789442bd4b8cfd1f2e8af7d461f1"

def fetch_bike_stations():
    try:
        response = requests.get(URL)  # Sending GET request
        response.raise_for_status()  # Raise error if request fails
        
        # Parse JSON response
        stations = response.json()
        
        # Print station details (first 5 stations for testing)
        print("\n🚲 Dublin Bikes Stations:\n")
        for station in stations[:5]:  # Limiting to 5 stations for readability
            print(f"Station: {station['name']}")
            print(f"Status: {station['status']}")
            print(f"Address: {station['address']}")
            print(f"Available Bikes: {station['available_bikes']}")
            print(f"Available Stands: {station['available_bike_stands']}")
            print("-" * 40)
        
        # Optionally save to a JSON file
        with open("dublin_bikes.json", "w") as file:
            json.dump(stations, file, indent=4)
        print("\n Data saved to 'dublin_bikes.json'.")

    except requests.exceptions.RequestException as e:
        print(f"\n API Request Failed: {e}")

# Run the function
fetch_bike_stations()
