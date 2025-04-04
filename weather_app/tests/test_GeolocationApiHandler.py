import os
import unittest
from dotenv import load_dotenv
from weather_app.handlers.GeolocationApiHandler import GeolocationApiHandler, ApiHandlerError

class TestGeolocationApiHandler(unittest.TestCase):

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

        cls.api_root = os.getenv("GEOCODING_API")
        cls.api_key = os.getenv("OPEN_WEATHER_API_KEY")  # reusing API key variable

        if not cls.api_root or not cls.api_key:
            raise Exception("GEOCODING_API or OPEN_WEATHER_API_KEY not set in .env files")

        # Instantiate the handler (dummy call is done in __init__)
        cls.handler = GeolocationApiHandler(cls.api_root, cls.api_key)

    def test_dummy_call(self):
        """
        The dummy call in __init__ should have set last_json.
        For the geocoding API, we expect a JSON array (list) as a response.
        """
        self.assertIsNotNone(self.handler.last_json)
        self.assertIsInstance(self.handler.last_json, list)
        self.assertGreaterEqual(len(self.handler.last_json), 1)

    def test_reverse_geocode_success(self):
        """
        Test reverse geocoding for a known location.
        For example, using Beijing's approximate coordinates.
        """
        # Beijing's approximate coordinates
        lat = 39.9042
        lon = 116.4074
        result = self.handler.reverse_geocode(lat, lon, limit=1)
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        # Check that the returned object contains a city name.
        self.assertIn("name", result[0])
        # Optionally, check if the name matches expected values (e.g., contains 'Beijing')
        self.assertIn("Beijing", result[0]["name"])

if __name__ == '__main__':
    unittest.main()
