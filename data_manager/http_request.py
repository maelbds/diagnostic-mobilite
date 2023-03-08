"""
http request used with API calls.
"""
import requests
import time


def get_request(headers, url):
    request_ok = False
    while not request_ok:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                request_ok = True
                return response
            elif response.status_code == 429:
                # Too many requests : need to wait a little
                time.sleep(5)
            elif response.status_code == 404:
                # If unknown geocode, INSEE's API returns 404
                # Used to raise UnknownGeocodeError in data_manager.insee.api_request
                return None
            else:
                print(response)
        except Exception as e:
            print(e)
            print("Connection Error. New Try.")


def post_request(url, query):
    request_ok = False
    while not request_ok:
        try:
            response = requests.post(url,
                                     data=query,
                                     headers={'content-type': 'application/json; charset=utf-8'},
                                     timeout=180)
            if response.status_code == 200:
                request_ok = True
                return response
            elif response.status_code == 429:
                #  https://overpass-api.de/api/status
                time.sleep(10)
            else:
                print(response)
        except Exception as e:
            print(e)
            print("Connection Error. New Try.")
