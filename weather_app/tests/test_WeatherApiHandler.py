import os
import time
import unittest
from datetime import datetime, timedelta
from dotenv import load_dotenv
from weather_app.handlers.WeatherApiHandler import (
    WeatherApiHandler, WeatherApiError
)

class TestWeatherApiHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Get the directory of the current file (inside tests)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up two levels to the main project folder
        project_dir = os.path.dirname(os.path.dirname(current_dir))
        # Construct the paths to the .env files
        env_local_path = os.path.join(project_dir, '.env.local')
        env_public_path = os.path.join(project_dir, '.env.public')

        # Check if files exist
        if not os.path.exists(env_local_path):
            raise FileNotFoundError(f".env.local not found at {env_local_path}")
        if not os.path.exists(env_public_path):
            raise FileNotFoundError(f".env.public not found at {env_public_path}")

        # Load environment variables from both files
        load_dotenv(env_local_path)
        load_dotenv(env_public_path)

        cls.api_root = os.getenv("OPEN_WEATHER_API")
        cls.api_key = os.getenv("OPEN_WEATHER_API_KEY")

        if not cls.api_root or not cls.api_key:
            raise Exception("OPEN_WEATHER_API or OPEN_WEATHER_API_KEY not set in .env files")

        # Instantiate the handler (dummy call is done in __init__)
        cls.handler = WeatherApiHandler(cls.api_root, cls.api_key)

    def test_dummy_call(self):
        # The dummy call in __init__ should have set last_json
        self.assertIsNotNone(self.handler.last_json)
        self.assertIn("cod", self.handler.last_json)
        self.assertEqual(self.handler.last_json.get("cod"), "200")

    def test_get_weather_n_days_into_future_by_date_success_with_city(self):
        # Use a start date from 2 days ago (formatted as mm/dd/yyyy)
        start_date = (datetime.now() - timedelta(days=2)).strftime("%m/%d/%Y")
        count = 2  # expecting data for the day of start_date and the following day
        result = self.handler.get_weather_n_days_into_future_by_date("London", None, None, start_date, count)
        self.assertIsInstance(result, dict)
        self.assertIn("cod", result)
        self.assertEqual(result.get("cod"), "200")

    def test_get_weather_n_days_into_future_by_date_success_with_coords(self):
        # Use a start date from 2 days ago and provide lat/lon instead of city.
        start_date = (datetime.now() - timedelta(days=2)).strftime("%m/%d/%Y")
        count = 2
        # Example coordinates for London (approximate)
        lat = 51.5074
        lon = -0.1278
        result = self.handler.get_weather_n_days_into_future_by_date("", lat, lon, start_date, count)
        self.assertIsInstance(result, dict)
        self.assertIn("cod", result)
        self.assertEqual(result.get("cod"), "200")

    def test_get_weather_n_days_into_past_by_date_success_with_city(self):
        # Use an end date from 1 day ago (formatted as mm/dd/yyyy)
        end_date = (datetime.now() - timedelta(days=1)).strftime("%m/%d/%Y")
        count = 2  # expecting data for the end day and the preceding day
        result = self.handler.get_weather_n_days_into_past_by_date("London", None, None, end_date, count)
        self.assertIsInstance(result, dict)
        self.assertIn("cod", result)
        self.assertEqual(result.get("cod"), "200")

    def test_get_weather_n_days_into_past_by_date_success_with_coords(self):
        # Use an end date from 1 day ago and provide lat/lon
        end_date = (datetime.now() - timedelta(days=1)).strftime("%m/%d/%Y")
        count = 2
        # Example coordinates for London (approximate)
        lat = 51.5074
        lon = -0.1278
        result = self.handler.get_weather_n_days_into_past_by_date("", lat, lon, end_date, count)
        self.assertIsInstance(result, dict)
        self.assertIn("cod", result)
        self.assertEqual(result.get("cod"), "200")

    def test_get_weather_by_interval_success_with_city(self):
        # Use an interval: start date 3 days ago, end date 2 days ago.
        start_date = (datetime.now() - timedelta(days=3)).strftime("%m/%d/%Y")
        end_date = (datetime.now() - timedelta(days=2)).strftime("%m/%d/%Y")
        result = self.handler.get_weather_by_interval("London", None, None, start_date, end_date)
        self.assertIsInstance(result, dict)
        self.assertIn("cod", result)
        self.assertEqual(result.get("cod"), "200")

    def test_get_weather_by_interval_success_with_coords(self):
        # Use an interval with coordinates: start date 3 days ago, end date 2 days ago.
        start_date = (datetime.now() - timedelta(days=3)).strftime("%m/%d/%Y")
        end_date = (datetime.now() - timedelta(days=2)).strftime("%m/%d/%Y")
        # Example coordinates for London (approximate)
        lat = 51.5074
        lon = -0.1278
        result = self.handler.get_weather_by_interval("", lat, lon, start_date, end_date)
        self.assertIsInstance(result, dict)
        self.assertIn("cod", result)
        self.assertEqual(result.get("cod"), "200")

    def test_get_weather_by_interval_start_after_end_error(self):
        # Provide an interval where start date is after end date.
        start_date = (datetime.now() - timedelta(days=1)).strftime("%m/%d/%Y")
        end_date = (datetime.now() - timedelta(days=3)).strftime("%m/%d/%Y")
        with self.assertRaises(WeatherApiError) as context:
            self.handler.get_weather_by_interval("London", None, None, start_date, end_date)
        self.assertIn("start date must be before end date", str(context.exception).lower())

    def test_get_weather_by_interval_future_end_error(self):
        # Provide an interval with an end date in the future.
        start_date = (datetime.now() - timedelta(days=3)).strftime("%m/%d/%Y")
        future_end_date = (datetime.now() + timedelta(days=1)).strftime("%m/%d/%Y")
        with self.assertRaises(WeatherApiError) as context:
            self.handler.get_weather_by_interval("London", None, None, start_date, future_end_date)
        self.assertIn("end time is in the future", str(context.exception).lower())

    def test_future_start_error(self):
        # Set a start date in the future (e.g., tomorrow) for the future data method.
        future_date = (datetime.now() + timedelta(days=1)).strftime("%m/%d/%Y")
        count = 1
        with self.assertRaises(WeatherApiError) as context:
            self.handler.get_weather_n_days_into_future_by_date("London", None, None, future_date, count)
        self.assertIn("future", str(context.exception).lower())

    def test_future_end_error(self):
        # Set an end date in the future (e.g., tomorrow) for the past data method.
        future_date = (datetime.now() + timedelta(days=1)).strftime("%m/%d/%Y")
        count = 1
        with self.assertRaises(WeatherApiError) as context:
            self.handler.get_weather_n_days_into_past_by_date("London", None, None, future_date, count)
        self.assertIn("future", str(context.exception).lower())

if __name__ == '__main__':
    unittest.main()
