import requests
import logging
import time
from threading import Thread
from queue import Queue

logging.basicConfig(level=logging.INFO)

BASE_URL = "http://35.200.185.69:8000"
DEFAULT_LIMIT = 100

names_set = set()
work_queue = Queue()

def fetch_names(query, version):
    endpoint = f"/{version}/autocomplete"
    offset = 0
    while True:
        params = {'query': query, 'limit': DEFAULT_LIMIT, 'offset': offset}
        response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        if response.status_code == 200:
            data = response.json()
            names = data.get('results', [])
            names_set.update(names)
            logging.info(f"Response: {data}")
            if len(names) < DEFAULT_LIMIT:
                break
            offset += DEFAULT_LIMIT
            if len(names) == DEFAULT_LIMIT:
                for name in names:
                    if len(name) > len(query):
                        next_char = name[len(query)].lower()
                        work_queue.put((query + next_char, version))
        elif response.status_code == 429:
            time.sleep(10)
        else:
            break

def worker():
    while True:
        item = work_queue.get()
        if item is None:
            break
        query, version = item
        fetch_names(query, version)
        work_queue.task_done()

threads = [Thread(target=worker) for _ in range(5)]
for t in threads:
    t.start()

versions = ['v1', 'v2', 'v3']
for version in versions:
    for char in 'abcdefghijklmnopqrstuvwxyz':
        work_queue.put((char, version))

work_queue.join()

for _ in range(5):
    work_queue.put(None)
for t in threads:
    t.join()

logging.info(f"Collected {len(names_set)} names")