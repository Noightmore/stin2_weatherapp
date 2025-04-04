# File: services/handler_factory.py

import os
import logging
from dotenv import load_dotenv
from weather_app.services.MongoHandler import MongoHandler
from weather_app.services.WeatherApiHandler import WeatherApiHandler
from weather_app.services.GeolocationApiHandler import GeolocationApiHandler

class HandlerFactory:
    def __init__(self, env_paths):
        """
        Initialize the HandlerFactory by loading environment variables from the provided .env files.

        :param env_paths: List of file paths to .env files.
        """
        self.env_paths = env_paths
        self._load_env_files()

    def _load_env_files(self):
        """
        Load environment variables from all provided .env files.
        """
        for env_file in self.env_paths:
            if os.path.exists(env_file):
                load_dotenv(env_file, override=True)
                logging.info(f"Loaded environment variables from {env_file}")
            else:
                logging.warning(f"Environment file not found: {env_file}")

    def get_mongo_handler(self):
        """
        Initialize and return a MongoHandler instance using environment variables.

        Expected environment variables:
          - MONGO_URL: MongoDB connection string.
          - MONGO_DB: (optional) Database name (default: "db_xd").
          - MONGO_RETENTION_LIMIT: (optional) Retention limit (default: 400000).
          - MONGO_DELETE_COUNT: (optional) Number of documents to delete when retention is triggered (default: 1000).

        :return: An instance of MongoHandler.
        """
        mongo_url = os.getenv("MONGO_URL")
        if not mongo_url:
            raise Exception("MONGO_URL not set in environment variables.")
        db_name = os.getenv("MONGO_DB", "db_xd")
        retention_limit = int(os.getenv("MONGO_DB_MAX_DOC_COUNT", "400000"))
        delete_count = int(os.getenv("MONGO_DB_RETENTION_DELETION_COUNT", "1000"))
        return MongoHandler(mongo_url, db_name, retention_limit=retention_limit, delete_count=delete_count)

    def get_weather_handler(self):
        """
        Initialize and return a WeatherApiHandler instance using environment variables.

        Expected environment variables:
          - OPEN_WEATHER_API: Root URL for the weather API.
          - OPEN_WEATHER_API_KEY: The API key.

        :return: An instance of WeatherApiHandler.
        """
        api_root = os.getenv("OPEN_WEATHER_API")
        api_key = os.getenv("OPEN_WEATHER_API_KEY")
        if not api_root or not api_key:
            raise Exception("OPEN_WEATHER_API or OPEN_WEATHER_API_KEY not set in environment variables.")
        return WeatherApiHandler(api_root, api_key)


    def get_geolocation_handler(self):
        """
        Initialize and return a GeolocationApiHandler instance using environment variables.

        Expected environment variables:
          - GEOCODING_API: Root URL for the geocoding API.
          - OPEN_WEATHER_API_KEY: The API key (used for geocoding as well).

        :return: An instance of GeolocationApiHandler.
        """
        api_root = os.getenv("GEOCODING_API")
        api_key = os.getenv("OPEN_WEATHER_API_KEY")
        if not api_root or not api_key:
            raise Exception("GEOCODING_API or OPEN_WEATHER_API_KEY not set in environment variables.")
        return GeolocationApiHandler(api_root, api_key)

# todo: add postgres handler; add all handler creation methods to this class