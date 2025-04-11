import unittest
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class TestAllPredictModels(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_all_station_predictions(self):
        total_stations = 117
        datetime_str = "2025-04-11T12:00"
        failed = []

        for station_id in range(1, total_stations + 1):
            response = self.client.get(f'/predict?station_id={station_id}&datetime={datetime_str}')
            
            if response.status_code != 200:
                failed.append((station_id, f"Status: {response.status_code}"))
                continue

            try:
                prediction = float(response.data.decode('utf-8'))
                if prediction < 0:
                    failed.append((station_id, "Negative prediction"))
            except Exception as e:
                failed.append((station_id, f"Error: {str(e)}"))

        if failed:
            print("\n❌ Failed Predictions:")
            for station_id, reason in failed:
                print(f"Station {station_id}: {reason}")
            self.fail(f"{len(failed)} station predictions failed.")
        else:
            print("\n✅ All 117 station predictions succeeded.")

if __name__ == '__main__':
    unittest.main()
