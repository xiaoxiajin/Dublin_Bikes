import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class TestStationAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_get_stations(self):
        # print("\nRunning test_get_stations...")
        response = self.client.get('/stations')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'number', response.data)
        # print("✅ test_get_stations passed.")

    def test_get_weather(self):
        # print("\nRunning test_get_weather...")
        response = self.client.get('/weather')
        self.assertEqual(response.status_code, 200)
        self.assertIn('temp', response.data.decode('utf-8'))
        # print("✅ test_get_weather passed.")

    def test_update_bikes(self):
        # print("\nRunning test_update_bikes...")
        response = self.client.get('/update_bikes')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'updated', response.data.lower())
        # print("✅ test_update_bikes passed.")

    def test_update_weather(self):
        # print("\nRunning test_update_weather...")
        response = self.client.get('/update_weather')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'updated', response.data.lower())
        # print("✅ test_update_weather passed.")

if __name__ == '__main__':
    unittest.main()

