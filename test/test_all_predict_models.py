import unittest
import pickle
import pandas as pd
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class TestAllStationTrend(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_station_trend_predictions(self):
        failed = []

        model_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'machine_learning/station_models'))
        available_model_ids = set()
        for filename in os.listdir(model_folder):
            if filename.startswith("station_") and filename.endswith(".pkl"):
                try:
                    sid = int(filename.split("_")[1].split(".")[0])
                    available_model_ids.add(sid)
                except:
                    continue

        print(f"\n🧪 Found {len(available_model_ids)} station models.")

        for station_id in sorted(available_model_ids):
            response = self.client.get(f'/station_prediction?station_id={station_id}')
            
            if response.status_code != 200:
                failed.append((station_id, f"Status: {response.status_code}"))
                continue

            try:
                trend_data = json.loads(response.data)
                if not isinstance(trend_data, list) or len(trend_data) == 0:
                    failed.append((station_id, "No trend data returned"))
                else:
                    for item in trend_data:
                        if "time" not in item or "bike_count" not in item:
                            failed.append((station_id, "Invalid trend data format"))
                            break
            except Exception as e:
                failed.append((station_id, f"Error parsing response: {str(e)}"))

        if failed:
            print("\nFailed station trends:")
            for station_id, reason in failed:
                print(f"Station {station_id}: {reason}")
            self.fail(f"{len(failed)} station trend tests failed.")
        else:
            print("\nAll station trend predictions passed.")

class TestModelPrediction(unittest.TestCase):
    def test_model_loading_and_prediction(self):
        station_id = 10
        model_path = f"machine_learning/station_models/station_{station_id}.pkl"
        self.assertTrue(os.path.exists(model_path), f"Model file not found: {model_path}")
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)

        test_input = pd.DataFrame([{
            
            "day": 1,
            "hour": 0,
            "avg_air_temp": 13.955,
            "avg_humidity": 83.75,
            "day_name": 6
        }])

        prediction = model.predict(test_input)
        self.assertIsInstance(prediction[0], float)

if __name__ == '__main__':
    unittest.main()
