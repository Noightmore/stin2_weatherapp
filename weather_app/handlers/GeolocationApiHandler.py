# File: handlers/GeolocationApiHandler.py

import requests
import logging
import json
from weather_app.handlers.ApiHandler import ApiHandler, ApiHandlerError

class GeolocationApiHandler(ApiHandler):
    def __init__(self, api_root, api_key):
        """
        Initialize the GeolocationApiHandler.

        :param api_root: The root URL for the geocoding API
                         (e.g., "http://api.openweathermap.org/geo/1.0/")
        :param api_key: The API key for the geocoding API.
        """
        super().__init__(api_root, api_key)
        logging.info("Initializing GeolocationApiHandler")

        # Optional: do a dummy call to verify connectivity.
        beijing_lat = 39.9042
        beijing_lon = 116.4074

        dummy_url = f"{self.api_root}reverse?lat={beijing_lat}&lon={beijing_lon}&limit=1&appid={self.api_key}"
        response = requests.get(dummy_url)
        if response.status_code != 200:
            self._handle_error(response)
        logging.info("Dummy call successful.")
        self.last_json = response.json()

    def reverse_geocode(self, lat, lon, limit=1):
        """
        Retrieve geolocation information via reverse geocoding.

        :param lat: Latitude.
        :param lon: Longitude.
        :param limit: Maximum number of results to return (default is 1).
        :return: The JSON response from the API.
        """
        url = f"{self.api_root}reverse?lat={lat}&lon={lon}&limit={limit}&appid={self.api_key}"
        logging.info(f"Calling reverse geocoding API: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            self._handle_error(response)
        self.last_json = response.json()
        return self.last_json
