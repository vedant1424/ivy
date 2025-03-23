import requests
import logging
import time
from threading import Thread, Semaphore
from queue import Queue

logging.basicConfig(level=logging.INFO)

BASE_URL = "http://35.200.185.69:8000"
DEFAULT_LIMIT = 100
MAX_RETRIES = 3
BASE_BACKOFF = 1
MAX_CONCURRENT = 5

names_set = set()
work_queue = Queue()
lock = Semaphore(1)
rate_limit_semaphore = Semaphore(MAX_CONCURRENT)

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_exhausted = False

tries = {'v1': TrieNode(), 'v2': TrieNode(), 'v3': TrieNode()}

def api_call(params, version):
    endpoint = f"/{version}/autocomplete"
    for attempt in range(MAX_RETRIES):
        try:
            with rate_limit_semaphore:
                response = requests.get(f"{BASE_URL}{endpoint}", params=params)
                if response.status_code == 200:
                    data = response.json()
                    logging.info(f"Response: {data}")
                    return data
                elif response.status_code == 429:
                    sleep_time = BASE_BACKOFF * (2 ** attempt)
                    logging.warning(f"Rate limited for version {version}. Waiting {sleep_time}s")
                    time.sleep(sleep_time)
                else:
                    return None
        except requests.exceptions.RequestException as e:
            time.sleep(BASE_BACKOFF * (2 ** attempt))
    return None

def process_prefix(prefix, version):
    trie_root = tries[version]
    current = trie_root
    for char in prefix:
        if char not in current.children:
            current.children[char] = TrieNode()
        current = current.children[char]
    if current.is_exhausted:
        return

    offset = 0
    while True:
        params = {'query': prefix, 'limit': DEFAULT_LIMIT, 'offset': offset}
        data = api_call(params, version)
        if data:
            names = data.get('results', [])
            with lock:
                names_set.update(names)
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

def main():
    threads = [Thread(target=worker) for _ in range(MAX_CONCURRENT)]
    for t in threads:
        t.start()

    versions = ['v1', 'v2', 'v3']
    # Expanded to include characters from v3 output
    for version in versions:
        for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()-_=+[{]};:\,<.>/?\\|`~अआइईउऊएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह1234567890।॥:':
            work_queue.put((char, version))

    work_queue.join()

    for _ in range(MAX_CONCURRENT):
        work_queue.put(None)
    for t in threads:
        t.join()

    with open("names.txt", "w") as f:
        for name in sorted(names_set):
            f.write(f"{name}\n")
    logging.info(f"Collected {len(names_set)} names")

if __name__ == "__main__":
    main()