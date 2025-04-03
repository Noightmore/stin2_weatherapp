# File: services/WeatherApiHandler.py

import os
import requests
import time
import logging
from datetime import datetime
import json


class WeatherApiHandler:
    def __init__(self, api_root, api_key):
        """
        Initialize the WeatherApiHandler.

        :param api_root: The root URL of the API (e.g., "https://history.openweathermap.org/data/2.5/history/")
        :param api_key: The API key string.
        """
        self.api_root = api_root.rstrip('/') + '/'
        self.api_key = api_key
        self.last_json = None
        logging.info("Initializing WeatherApiHandler")

        # check if the API key is set
        if not self.api_key:
            raise ValueError("API key is not set. Check your .env file!")

        # Check if the API root URL is set
        if not self.api_root:
            raise ValueError("API root URL is not set. Check your .env file!")

        # Do a dummy call to verify connectivity and key validity.
        # get current time in unix timestamp - 1 day
        now = int(time.time()) - 86400
        dummy_url = f"{self.api_root}city?q=London&start={now}&cnt=1&appid={self.api_key}&type=daily"
        response = requests.get(dummy_url)
        self.last_json = response.json()
        if response.status_code != 200:
            self._handle_error(response)
        logging.info("Dummy call successful.")


    def _handle_error(self, response):
        """
        Raise an appropriate exception based on the API response status code.
        """
        code = response.status_code
        # You can parse additional details from response.json() if needed.
        try:
            error_info = response.json()
        except Exception:
            error_info = {}
        if code == 400:
            raise BadRequestError(f"400 - Bad Request: {error_info.get('message', 'Missing or incorrect parameters')}")
        elif code == 401:
            raise UnauthorizedError("401 - Unauthorized: API token missing or invalid for this API")
        elif code == 404:
            raise NotFoundError("404 - Not Found: No data found for the requested parameters")
        elif code == 429:
            raise TooManyRequestsError("429 - Too Many Requests: API quota exceeded")
        elif 500 <= code < 600:
            raise UnexpectedError(f"{code} - Unexpected Error: Contact support with details of your API request")
        else:
            raise WeatherApiError(f"{code} - Unexpected error (wtf?): {error_info}")


    def get_weather_n_days_into_future_by_date(self, city, start, count, occurrence_type="daily"):
        """
        Call the weather API for a given city and start time.

        :param city: Name of the city.
        :param start: Unix timestamp for the start (must not be in the future).
        :param count: Number of days (data for count days from start).
                      (The end date must not be in the future.)
        :param occurrence_type: Type of forecast. Default is "daily".
        :return: The JSON response from the API.
        """

        # start is a date in mm/dd/yyyy format
        # convert to unix timestamp
        start = int(time.mktime(datetime.strptime(start, "%m/%d/%Y").timetuple()))

        now = int(time.time())
        if start > now:
            raise WeatherApiError("Start time is in the future.")

        # Check if the requested range goes into the future.
        if start + count * 86400 > now:
            raise WeatherApiError("Requested data range goes into the future.")

        url = f"{self.api_root}city?q={city}&start={start}&cnt={count}&appid={self.api_key}&type={occurrence_type}"
        logging.info(f"Calling API: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            self._handle_error(response)
        self.last_json = response.json()
        return response.json()


    def get_weather_n_day_into_past_by_date(self, city, end, count, occurrence_type="daily"):
        """
        A method for calling the weather API for a given city n days into the past since a given end date.

        :param city: Name of the city.
        :param end: Unix timestamp for the end.
        :param count: Number of days of data.
        :param occurrence_type: Type of forecast (default: "daily").
        :return: The JSON response from the API.
        """

        # end is a date in mm/dd/yyyy format
        # convert to unix timestamp
        end = int(time.mktime(datetime.strptime(end, "%m/%d/%Y").timetuple()))

        now = int(time.time())

        if end > now:
            raise WeatherApiError("End time is in the future.")

        start = end - count * 86400

        url = f"{self.api_root}city?q={city}&start={start}&cnt={count}&appid={self.api_key}&type={occurrence_type}"
        logging.info(f"Calling API: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            self._handle_error(response)
        self.last_json = response.json()
        return response.json()


    def get_last_json(self):
        """
        Return the last JSON response received from the API. Nicely formatted.
        """
        formatted_json = json.dumps(self.last_json, indent=4, sort_keys=True)
        return formatted_json


class WeatherApiError(Exception):
    """Base exception for Weather API errors."""
    pass

class BadRequestError(WeatherApiError):
    pass

class UnauthorizedError(WeatherApiError):
    pass

class NotFoundError(WeatherApiError):
    pass

class TooManyRequestsError(WeatherApiError):
    pass

class UnexpectedError(WeatherApiError):
    pass