# CF-Lens

CF-Lens is a small CLI tool I built to analyze my Codeforces activity.
It fetches submission data using the Codeforces API and generates a dashboard with useful insights like rating progress, problem difficulty, activity patterns, and weak topics.

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

* Console:

```text
Weak Topics:
- dp (32.5% success, 40 attempts)
- graphs (41.2% success, 25 attempts)
```

* Output:

```text
output/<your-handle>_dashboard.png
```
---

## Project Structure

```text
CF-Lens/
│
├── src/
│   ├── fetcher.py      # API calls
│   ├── processor.py    # data processing + analysis
│   ├── visualizer.py   # dashboard creation
│
├── tests/
│   └── test_processor.py
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

So I built this as a small personal analytics tool.

---

## Notes

* Some problems don’t have ratings, so they are handled separately
* Data depends on Codeforces API availability
* Works best with users who have a decent number of submissions

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
