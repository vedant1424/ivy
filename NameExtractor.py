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

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_exhausted = False

tries = {'v1': TrieNode(), 'v2': TrieNode(), 'v3': TrieNode()}

def process_prefix(prefix, version):
    trie_root = tries[version]
    current = trie_root
    for char in prefix:
        if char not in current.children:
            current.children[char] = TrieNode()
        current = current.children[char]
    if current.is_exhausted:
        return

    endpoint = f"/{version}/autocomplete"
    offset = 0
    while True:
        params = {'query': prefix, 'limit': DEFAULT_LIMIT, 'offset': offset}
        response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        if response.status_code == 200:
            data = response.json()
            names = data.get('results', [])
            names_set.update(names)
            logging.info(f"Response: {data}")
            if len(names) < DEFAULT_LIMIT:
                current.is_exhausted = True
                break
            offset += DEFAULT_LIMIT
            if len(names) == DEFAULT_LIMIT:
                for name in names:
                    if len(name) > len(prefix):
                        next_char = name[len(prefix)].lower()
                        if next_char not in current.children:
                            work_queue.put((prefix + next_char, version))
        elif response.status_code == 429:
            time.sleep(10)
        else:
            break

def worker():
    while True:
        item = work_queue.get()
        if item is None:
            break
        prefix, version = item
        process_prefix(prefix, version)
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