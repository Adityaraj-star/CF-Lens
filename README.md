# CF-Lens

![tests](https://github.com/Adityaraj-star/CF-Lens/actions/workflows/tests.yml/badge.svg)

CF-Lens is a small CLI tool I built to analyze my Codeforces activity.
It fetches submission data using the Codeforces API, finds patterns in it, and generates a dashboard with useful insights like rating progress, problem difficulty, activity patterns, and weak topics. It also recommends problems to practice based on what you're actually bad at.

---

## Features

* Fetches up to 10,000 submissions from Codeforces
* Generates a multi-panel dashboard using Matplotlib
* Shows:

  * Rating progression
  * Verdict breakdown
  * Problem difficulty distribution
  * Activity heatmap (day × hour)
  * Submissions per month
  * Language usage
  * Top problem tags
  * Rating change per contest
* Detects weak topics based on success rate
* Recommends practice problems for your weak topics, filtered by your current rating so they're actually solvable
* Caches API responses locally so repeated runs are faster and don't hammer the Codeforces API

---

## How to Run

Clone the repo and install dependencies:

```bash
pip install -r requirements.txt
```

Run the project:

```bash
python main.py
```

Then enter your Codeforces handle when prompted.

The dashboard will be saved in the `output/` folder.

---

## Example Output

Console:

```text
Weak Topics:
- dp (32.5% success, 40 attempts)
- graphs (41.2% success, 25 attempts)

Recommended Practice Problems:

  dp:
    - Simple Skewness (1400) -> https://codeforces.com/problemset/problem/1946/A
    - Painting Fence (1500) -> https://codeforces.com/problemset/problem/448/C

  graphs:
    - Bipartite Checking (1400) -> https://codeforces.com/problemset/problem/862/B
```

Output file:

```text
output/_dashboard.png
```

---

## How the Recommendations Work

I didn't want it to just tell me I'm bad at DP, I already know that. So once it finds a weak topic, it pulls the full Codeforces problem set and filters it down to:

* problems tagged with that topic
* rated close to my current rating (not way below, not way above)
* problems I haven't already solved

That last part needed a bit of care — Codeforces problem *names* aren't unique across contests, so I couldn't just match on the name. I ended up using `contestId + index` (like `1946A`) as the actual unique ID for a problem, both when tracking what I've solved and when filtering the recommendation pool.

---

## Caching

Every run used to re-fetch the full problem set from Codeforces even though it barely changes. Now it's cached locally as JSON with a timestamp, so:

* the problem set is reused for 24 hours
* a user's submissions/contests are reused for 1 hour

Cache files live in `.cf_cache/` and are gitignored — it's just local scratch data, nothing to commit.

---

## Project Structure

```text
CF-Lens/
│
├── src/
│   ├── fetcher.py       # API calls + caching
│   ├── processor.py     # data processing + analysis
│   ├── recommender.py   # weak-topic-based problem recommendations
│   ├── cache.py         # simple TTL-based local cache
│   ├── visualizer.py    # dashboard creation
│
├── tests/
│   ├── test_processor.py
│   └── test_recommender.py
│
├── .github/workflows/
│   └── tests.yml        # runs pytest on every push/PR
│
├── output/
├── requirements.txt
├── main.py
└── README.md
```

---

## Why I Built This

I wanted a better way to understand my Codeforces performance beyond just rating.
Especially things like:

* which topics I struggle with
* when I am most active
* how my problem difficulty is changing over time

Just seeing "you're weak at DP" wasn't useful on its own though, so I added the recommendation part to actually turn that into something I can act on.

---

## Notes

* Some problems don't have ratings, so they are handled separately
* Data depends on Codeforces API availability
* Works best with users who have a decent number of submissions
* Recommendations depend on there being unrated-appropriate problems left in your weak tags — if you've solved most of what's near your rating for a topic, it may come back empty

---

## Future Improvements

* Compare two users
* Add streak detection
* Export report as PDF
* Maybe build a simple web UI

---

## Tech Stack

* Python
* Pandas
* Matplotlib
* Codeforces API
* pytest + GitHub Actions