import unittest

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class TestStationRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_get_api_key(self):
        res = self.client.get('/get_api_key')
        self.assertEqual(res.status_code, 200)
        self.assertIn('api_key', res.json)

    def test_get_stations(self):
        res = self.client.get('/stations')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json, list)

    def test_get_availability(self):
        res = self.client.get('/availability')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json, list)

    def test_get_station_data(self):
        res = self.client.get('/station_data')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json, list)

    def test_station_prediction_valid(self):
        res = self.client.get('/station_prediction?station_id=10')
        self.assertEqual(res.status_code, 200)
        self.assertIn('bike_count', res.json[0])

    def test_station_prediction_missing_id(self):
        res = self.client.get('/station_prediction?station_id=')
        self.assertEqual(res.status_code, 400)
        self.assertIn('error', res.json)

    def test_station_prediction_not_found(self):
        res = self.client.get('/station_prediction?station_id=999999')
        self.assertIn(res.status_code, [404, 500])  # may vary
        self.assertIn('error', res.json)

    def test_station_prediction_prediction(self):
        res = self.client.get('/station_prediction?station_id=10')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json, list)
        self.assertIn('bike_count', res.json[0])

if __name__ == '__main__':
    unittest.main()
