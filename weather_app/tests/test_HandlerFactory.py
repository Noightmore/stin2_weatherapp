import os
import unittest
from dotenv import load_dotenv
from weather_app.helpers.HandlerFactory import HandlerFactory
from weather_app.services.MongoHandler import MongoHandler
from weather_app.services.WeatherApiHandler import WeatherApiHandler
from weather_app.services.GeolocationApiHandler import GeolocationApiHandler

class TestHandlerFactory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Get the directory of this test file (inside tests)
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
        # Initialize the HandlerFactory with the paths
        cls.env_paths = [env_local_path, env_public_path]
        cls.factory = HandlerFactory(cls.env_paths)

    def test_get_mongo_handler(self):
        mongo_handler = self.factory.get_mongo_handler()
        self.assertIsInstance(mongo_handler, MongoHandler)
        # Optionally verify connection (if desired)
        self.assertTrue(mongo_handler.verify_connection())

    def test_get_weather_handler(self):
        weather_handler = self.factory.get_weather_handler()
        self.assertIsInstance(weather_handler, WeatherApiHandler)
        # Check that a dummy call was made and last_json is set
        self.assertIsNotNone(weather_handler.last_json)
        self.assertEqual(weather_handler.last_json.get("cod"), "200")

    def test_get_geolocation_handler(self):
        geolocation_handler = self.factory.get_geolocation_handler()
        self.assertIsInstance(geolocation_handler, GeolocationApiHandler)
        # Check that a dummy call was made and last_json is set
        self.assertIsNotNone(geolocation_handler.last_json)
        self.assertIsInstance(geolocation_handler.last_json, list)
        self.assertGreaterEqual(len(geolocation_handler.last_json), 1)

if __name__ == '__main__':
    unittest.main()
