import requests
import logging
import time
from threading import Thread, Semaphore
from queue import Queue

# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
BASE_URL = "http://35.200.185.69:8000"
DEFAULT_LIMIT = 100
MAX_RETRIES = 3
BASE_BACKOFF = 1
MAX_CONCURRENT = 5

# Dictionary to store names for each version
names_sets = {
    'v1': set(),
    'v2': set(),
    'v3': set()
}

# Dictionary to track API calls for each version
api_calls = {
    'v1': 0,
    'v2': 0,
    'v3': 0
}

# Threading utilities
work_queue = Queue()
lock = Semaphore(1)
rate_limit_semaphore = Semaphore(MAX_CONCURRENT)

# Trie node for prefix tracking
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_exhausted = False

# Separate tries for each version
tries = {
    'v1': TrieNode(),
    'v2': TrieNode(),
    'v3': TrieNode()
}

def api_call(params, version):
    """Make an API call for a specific version and track the call count."""
    global api_calls
    endpoint = f"/{version}/autocomplete"
    for attempt in range(MAX_RETRIES):
        try:
            with rate_limit_semaphore:
                response = requests.get(f"{BASE_URL}{endpoint}", params=params)
                api_calls[version] += 1  # Increment call count for this version
                if response.status_code == 200:
                    data = response.json()
                    logging.info(f"Response for {version}: {data}")
                    return data
                elif response.status_code == 429:
                    sleep_time = BASE_BACKOFF * (2 ** attempt)
                    logging.warning(f"Rate limited for {version}. Waiting {sleep_time}s")
                    time.sleep(sleep_time)
                else:
                    return None
        except requests.exceptions.RequestException as e:
            time.sleep(BASE_BACKOFF * (2 ** attempt))
    return None

def process_prefix(prefix, version):
    """Process a prefix for a given version, updating its name set."""
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
                names_sets[version].update(names)  # Add names to version-specific set
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
    """Worker thread to process items from the queue."""
    while True:
        item = work_queue.get()
        if item is None:
            break
        prefix, version = item
        process_prefix(prefix, version)
        work_queue.task_done()

def main():
    """Main function to orchestrate the name extraction."""
    # Start worker threads
    threads = [Thread(target=worker) for _ in range(MAX_CONCURRENT)]
    for t in threads:
        t.start()

    # Queue initial prefixes for each version
    versions = ['v1', 'v2', 'v3']
    #using a modified version of initial_char used from uniquechars.py that uses the known chars from previous testing to minimize the number 0f api calls. 
    # for all the chars use -> abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -+.
    initial_chars = '0 .rm134cx+uv-8gq2lpdeh6ijk9tazyw75nfosb'
    for version in versions:
        for char in initial_chars:
            work_queue.put((char, version))

    # Wait for all tasks to complete
    work_queue.join()

    # Shutdown threads
    for _ in range(MAX_CONCURRENT):
        work_queue.put(None)
    for t in threads:
        t.join()

    # Build name_versions dictionary
    name_versions = {}
    for version in versions:
        for name in names_sets[version]:
            if name not in name_versions:
                name_versions[name] = set()
            name_versions[name].add(version)

    # Calculate statistics
    total_unique = len(name_versions)
    names_in_one = sum(1 for v in name_versions.values() if len(v) == 1)
    names_in_two = sum(1 for v in name_versions.values() if len(v) == 2)
    

    # Save names to version-specific files
    for version in versions:
        with open(f"names_{version}.txt", "w") as f:
            for name in sorted(names_sets[version]):
                f.write(f"{name}\n")

    # Generate and log detailed report
    total_names = sum(len(names_sets[version]) for version in versions)
    total_calls = sum(api_calls[version] for version in versions)
    report = "\nDetailed Report:\n"
    for version in versions:
        report += f"{version.upper()}:\n"
        report += f"  Names Collected: {len(names_sets[version])}\n"
        report += f"  API Calls: {api_calls[version]}\n"
    report += f"\nTotal Names Collected (sum): {total_names}\n"
    report += f"Total API Calls: {total_calls}\n"
    report += f"Total Unique Names: {total_unique}\n"
    report += f"Names in Exactly One Version: {names_in_one}\n"
    report += f"Names in Exactly Two Versions: {names_in_two}\n"
    logging.info(report)

if __name__ == "__main__":
    main()