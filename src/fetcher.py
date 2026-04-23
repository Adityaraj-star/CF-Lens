import time
import requests

BASE_URL = "https://codeforces.com/api"
TIMEOUT = 10
RETRIES = 3


def _make_request(endpoint, params):
    url = f"{BASE_URL}/{endpoint}"

    for i in range(RETRIES):
        try:
            res = requests.get(url, params=params, timeout=TIMEOUT)
        except requests.exceptions.ConnectionError:
            raise RuntimeError("No internet connection. Check your network and try again.")
        except requests.exceptions.Timeout:
            raise RuntimeError("Request timed out.")

        if res.status_code == 429:
            time.sleep(2 * (i + 1))
            continue

        if res.status_code != 200:
            raise RuntimeError(f"HTTP {res.status_code} from Codeforces API.")

        data = res.json()

        if data["status"] != "OK":
            raise RuntimeError("Something went wrong with Codeforces API")

        return data["result"]

    raise RuntimeError("Too many retries, try again later")


def fetch_user_info(handle):
    results = _make_request("user.info", {"handles": handle})

    if not results:
        raise RuntimeError(f"Handle '{handle}' not found on Codeforces.")

    user = results[0]
    user.setdefault("firstName", "")
    user.setdefault("lastName", handle)
    user.setdefault("rating", None)
    user.setdefault("rank", "unrated")
    user.setdefault("maxRating", None)
    user.setdefault("maxRank", "unrated")

    return user


def fetch_submissions(handle, count=10000):
    data = _make_request("user.status", {"handle": handle, "count": count})
    return [s for s in data if "problem" in s]


def fetch_contest_history(handle):
    return _make_request("user.rating", {"handle": handle})