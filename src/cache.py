import json
import os
import time

CACHE_DIR = ".cf_cache"


def _path(key):
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"{key}.json")


def get(key, ttl):
    path = _path(key)

    if not os.path.exists(path):
        return None

    with open(path) as f:
        payload = json.load(f)

    if time.time() - payload["ts"] > ttl:
        return None

    return payload["data"]


def set(key, data):
    path = _path(key)
    with open(path, "w") as f:
        json.dump({"ts": time.time(), "data": data}, f)