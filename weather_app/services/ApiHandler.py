# File: services/ApiHandler.py

import requests
import logging
import json

class ApiHandler:
    def __init__(self, api_root, api_key):
        """
        Initialize the API handler with a root URL and API key.
        """
        self.api_root = api_root.rstrip('/') + '/'
        self.api_key = api_key
        self.last_json = None

        if not self.api_key:
            raise ValueError("API key is not set. Check your .env file!")
        if not self.api_root:
            raise ValueError("API root URL is not set. Check your .env file!")

    def _handle_error(self, response):
        """
        Raise an appropriate exception based on the API response status code.
        """
        code = response.status_code
        try:
            error_info = response.json()
        except Exception:
            error_info = {}
        if code == 400:
            raise BadRequestError(f"400 - Bad Request: {error_info.get('message', 'Missing or incorrect parameters')}")
        elif code == 401:
            raise UnauthorizedError("401 - Unauthorized: API token missing or invalid for this API")
        elif code == 404:
            raise NotFoundError(f"404 - Not Found: No data found for the requested parameters {error_info}")
        elif code == 429:
            raise TooManyRequestsError("429 - Too Many Requests: API quota exceeded")
        elif 500 <= code < 600:
            raise UnexpectedError(f"{code} - Unexpected Error: Contact support with details of your API request")
        else:
            raise ApiHandlerError(f"{code} - Unexpected error (wtf?): {error_info}")

    def get_last_json(self):
        """
        Return the last JSON response received from the API, formatted nicely.
        """
        return json.dumps(self.last_json, indent=4, sort_keys=True)


# Custom exceptions
class ApiHandlerError(Exception):
    pass

class BadRequestError(ApiHandlerError):
    pass

class UnauthorizedError(ApiHandlerError):
    pass

class NotFoundError(ApiHandlerError):
    pass

class TooManyRequestsError(ApiHandlerError):
    pass

class UnexpectedError(ApiHandlerError):
    pass