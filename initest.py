import requests
import logging

logging.basicConfig(level=logging.INFO)

BASE_URL = "http://35.200.185.69:8000"
API_ENDPOINT = "/v1/autocomplete"

response = requests.get(f"{BASE_URL}{API_ENDPOINT}?query=a")
logging.info(f"Response: {response.json()}")