import requests
import logging

logging.basicConfig(level=logging.INFO)

BASE_URL = "http://35.200.185.69:8000"

names_set = set()

def fetch_names(query, version='v1'):
    endpoint = f"/{version}/autocomplete"
    response = requests.get(f"{BASE_URL}{endpoint}?query={query}")
    if response.status_code == 200:
        data = response.json()
        names = data.get('results', [])
        names_set.update(names)
        logging.info(f"Response: {data}")
    else:
        logging.error(f"Failed to fetch names for {query} in version {version}")

fetch_names('a', version='v1')
logging.info(f"Collected {len(names_set)} names")