import requests

ZIP_CODE_API_KEY = "z1LAdcyZSdn6RKtZrjrYnJFQfiNd88WJJBcjRy2SxhYIcd2xDkUoLJr8J4TKazQP"
ZIP_CODE_URL = "https://www.zipcodeapi.com/rest/"


def get_zip_codes_for_city_and_state(city: str, state:str) -> list:
    """Execute GET API call to get ZIP Code for a given city and state"""
    url = f"{ZIP_CODE_URL}/{ZIP_CODE_API_KEY}/city-zips.json/{city}/{state}"
    response = requests.get(url)
    return response.json()['zip_codes']