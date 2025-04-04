# File: services/WeatherApiHandler.py

import os
import requests
import time
import logging
from datetime import datetime
import json
from weather_app.services.ApiHandler import ApiHandler, ApiHandlerError, BadRequestError, UnauthorizedError, \
    NotFoundError, TooManyRequestsError, UnexpectedError


class WeatherApiHandler(ApiHandler):
    def __init__(self, api_root, api_key):
        """
        Initialize the WeatherApiHandler.

        :param api_root: The root URL of the API (e.g., "https://history.openweathermap.org/data/2.5/history/")
        :param api_key: The API key string.
        """
        super().__init__(api_root, api_key)
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


    # def _handle_error(self, response):
    #     """
    #     Raise an appropriate exception based on the API response status code.
    #     """
    #     code = response.status_code
    #     # You can parse additional details from response.json() if needed.
    #     try:
    #         error_info = response.json()
    #     except Exception:
    #         error_info = {}
    #     if code == 400:
    #         raise BadRequestError(f"400 - Bad Request: {error_info.get('message', 'Missing or incorrect parameters')}")
    #     elif code == 401:
    #         raise UnauthorizedError("401 - Unauthorized: API token missing or invalid for this API")
    #     elif code == 404:
    #         raise NotFoundError(f"404 - Not Found: No data found for the requested parameters {error_info}")
    #     elif code == 429:
    #         raise TooManyRequestsError("429 - Too Many Requests: API quota exceeded")
    #     elif 500 <= code < 600:
    #         raise UnexpectedError(f"{code} - Unexpected Error: Contact support with details of your API request")
    #     else:
    #         raise WeatherApiError(f"{code} - Unexpected error (wtf?): {error_info}")


    def get_weather_n_days_into_future_by_date(self, city, latitude, longitude, start, count, occurrence_type="daily"):
        """
        Call the weather API for a given location starting from the provided start date.
        
        If a city is provided, it will be used in the query; if not, the query will use the
        latitude and longitude.

        :param city: Name of the city (if provided, used for the API call).
        :param latitude: Latitude (used if city is not provided).
        :param longitude: Longitude (used if city is not provided).
        :param start: Date string in "mm/dd/yyyy" format representing the start day.
        :param count: Number of days (data for count days from start). The range must not extend into the future.
        :param occurrence_type: Type of forecast. Default is "daily".
        :return: The JSON response from the API.
        """
        # Convert the start date string to a Unix timestamp.
        start_ts = int(time.mktime(datetime.strptime(start, "%m/%d/%Y").timetuple()))
        now = int(time.time())

        if start_ts > now:
            raise WeatherApiError("Start time is in the future.")
        if start_ts + count * 86400 > now:
            raise WeatherApiError("Requested data range goes into the future.")

        # Build URL based on whether city is provided.
        if city:
            url = f"{self.api_root}city?q={city}&start={start_ts}&cnt={count}&appid={self.api_key}&type={occurrence_type}"
        else:
            url = f"{self.api_root}city?lat={latitude}&lon={longitude}&start={start_ts}&cnt={count}&appid={self.api_key}&type={occurrence_type}"

        logging.info(f"Calling API: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            self._handle_error(response)
        self.last_json = response.json()
        return self.last_json



    def get_weather_n_days_into_past_by_date(self, city, latidue, longtidue, end, count, occurrence_type="daily"):
        """
        Retrieve weather data for a given location for a specified number of days ending at a given end date.

        If 'city' is provided, it is used in the query; otherwise, the latitude and longitude are used.

        :param city: Name of the city (if provided).
        :param latidue: Latitude (used if city is not provided).
        :param longtidue: Longitude (used if city is not provided).
        :param end: Date string in "mm/dd/yyyy" format representing the end day.
        :param count: Number of days of data to retrieve. Data will cover count days ending on the end date.
        :param occurrence_type: Type of forecast (default: "daily").
        :return: The JSON response from the API.
        """
        # Convert the end date from "mm/dd/yyyy" to a Unix timestamp.
        end_ts = int(time.mktime(datetime.strptime(end, "%m/%d/%Y").timetuple()))
        now = int(time.time())
        if end_ts > now:
            raise WeatherApiError("End time is in the future.")

        # Compute the start timestamp so that the data covers 'count' days ending at 'end_ts'.
        start_ts = end_ts - count * 86400

        # Build the URL: if city is provided, use that; otherwise use latitude and longitude.
        if city:
            url = f"{self.api_root}city?q={city}&start={start_ts}&cnt={count}&appid={self.api_key}&type={occurrence_type}"
        else:
            url = f"{self.api_root}city?lat={latidue}&lon={longtidue}&start={start_ts}&cnt={count}&appid={self.api_key}&type={occurrence_type}"

        logging.info(f"Calling API: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            self._handle_error(response)
        self.last_json = response.json()
        return self.last_json


    def get_weather_by_interval(self, city, latitude, longitude, start, end, occurrence_type="daily"):
        """
        Retrieve weather data for a given location for an interval specified by start and end dates.

        Both start and end should be date strings in "mm/dd/yyyy" format.
        If a city is provided (non-empty), it will be used; otherwise, the latitude and longitude
        will be used to identify the location.

        :param city: Name of the city (if provided).
        :param latitude: Latitude (used if city is not provided).
        :param longitude: Longitude (used if city is not provided).
        :param start: Start date as a string in "mm/dd/yyyy" format.
        :param end: End date as a string in "mm/dd/yyyy" format.
        :param occurrence_type: Type of forecast (default: "daily").
        :return: The JSON response from the API.
        """
        # Convert start and end date strings to Unix timestamps.
        start_ts = int(time.mktime(datetime.strptime(start, "%m/%d/%Y").timetuple()))
        end_ts = int(time.mktime(datetime.strptime(end, "%m/%d/%Y").timetuple()))

        # Validate that the interval is proper.
        if start_ts >= end_ts:
            raise WeatherApiError("Start date must be before end date.")

        now = int(time.time())
        if end_ts > now:
            raise WeatherApiError("End time is in the future.")

        # Build URL based on whether city is provided.
        if city:
            url = f"{self.api_root}city?q={city}&start={start_ts}&end={end_ts}&appid={self.api_key}&type={occurrence_type}"
        else:
            url = f"{self.api_root}city?lat={latitude}&lon={longitude}&start={start_ts}&end={end_ts}&appid={self.api_key}&type={occurrence_type}"

        logging.info(f"Calling API by interval: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            self._handle_error(response)
        self.last_json = response.json()
        return self.last_json


class WeatherApiError(ApiHandlerError):
    """Base exception for Weather API errors."""
    pass