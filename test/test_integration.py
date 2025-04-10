import unittest
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_bike_data_flow(self):
        update_response = self.client.get('/update_bikes')
        self.assertEqual(update_response.status_code, 200)
        self.assertIn(b'updated', update_response.data.lower())

        stations_response = self.client.get('/stations')
        self.assertEqual(stations_response.status_code, 200)
        data = json.loads(stations_response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn('number', data[0])

    def test_weather_data_flow(self):
        update_response = self.client.get('/update_weather')
        self.assertEqual(update_response.status_code, 200)
        self.assertIn(b'updated', update_response.data.lower())

        weather_response = self.client.get('/weather')
        self.assertEqual(weather_response.status_code, 200)
        data = json.loads(weather_response.data)
        self.assertIn('temp', data)
        self.assertIn('humidity', data)

if __name__ == '__main__':
    unittest.main()
