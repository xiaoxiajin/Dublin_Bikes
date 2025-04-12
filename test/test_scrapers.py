import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the module path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from website import scraper_dublin_bike, scraper_weather
from website.scraper_dublin_bike import fetch_bike_stations
from website.scraper_weather import safe_query_weatherAPI


class TestScraperFunctions(unittest.TestCase):

    @patch('website.scraper_dublin_bike.requests.get')
    def test_fetch_bike_stations_empty_list(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = []
        fetch_bike_stations()
        self.assertTrue(mock_get.called)

    @patch('website.scraper_dublin_bike.requests.get')
    def test_fetch_bike_stations_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "number": 1,
            "name": "Mock Station",
            "address": "Fake Street",
            "position": {"lat": 53.3, "lng": -6.2},
            "banking": True,
            "bike_stands": 20,
            "available_bikes": 5,
            "available_bike_stands": 15,
            "last_update": 1682300000000,
            "status": "OPEN"
        }]
        mock_get.return_value = mock_response

        fetch_bike_stations()
        self.assertTrue(mock_get.called)

    @patch('website.scraper_dublin_bike.requests.get', side_effect=Exception("API failure"))
    def test_fetch_bike_stations_failure(self, mock_get):
        with self.assertRaises(Exception) as context:
            fetch_bike_stations()
        self.assertIn("API failure", str(context.exception))

    @patch('website.scraper_weather.query_weatherAPI')
    def test_safe_weather_query_runs(self, mock_query):
        safe_query_weatherAPI()
        mock_query.assert_called_once()

    @patch('website.scraper_weather.query_weatherAPI', side_effect=Exception("Weather error"))
    def test_safe_weather_query_handles_exception(self, mock_query):
        with self.assertRaises(Exception) as context:
            safe_query_weatherAPI()
        self.assertIn("Weather error", str(context.exception))


if __name__ == '__main__':
    unittest.main()
