import pandas as pd
import numpy as np


def process_submissions(raw):
    if len(raw) == 0:
        return pd.DataFrame()

    rows = []
    for s in raw:
        prob = s.get("problem", {})
        rows.append({
            "sub_id":      s.get("id"),
            "timestamp":   s.get("creationTimeSeconds"),
            "verdict":     s.get("verdict", "UNKNOWN"),
            "language":    s.get("programmingLanguage", "Unknown"),
            "prob_name":   prob.get("name", "Unknown"),
            "contest_id":  prob.get("contestId"),
            "prob_index":  prob.get("index"),
            "prob_id":     f"{prob.get('contestId')}{prob.get('index')}",
            "prob_rating": prob.get("rating"),
            "tags":        prob.get("tags", []),
        })

    df = pd.DataFrame(rows)

    # datetime columns
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    df["hour"]     = df["datetime"].dt.hour
    df["weekday"]  = df["datetime"].dt.day_name()
    df["month"]    = df["datetime"].dt.to_period("M").astype(str)
    df["year"]     = df["datetime"].dt.year
    df["date"]     = df["datetime"].dt.date

    # verdict mapping - all major CF verdicts covered
    verdict_map = {
        "OK":                    "Accepted",
        "WRONG_ANSWER":          "Wrong Answer",
        "TIME_LIMIT_EXCEEDED":   "TLE",
        "MEMORY_LIMIT_EXCEEDED": "MLE",
        "RUNTIME_ERROR":         "Runtime Error",
        "COMPILATION_ERROR":     "Compilation Error",
        "SKIPPED":               "Skipped",
        "CHALLENGED":            "Challenged",
        "PARTIAL":               "Partial",
    }
    df["verdict_label"] = df["verdict"].map(verdict_map).fillna("Other")

    # difficulty buckets
    df["prob_rating"] = pd.to_numeric(df["prob_rating"], errors="coerce")
    df["difficulty_bucket"] = pd.cut(
        df["prob_rating"],
        bins=[0, 900, 1200, 1500, 1800, 2100, 2400, 4000],
        labels=["≤900", "1000-1200", "1200-1500", "1500-1800",
                "1800-2100", "2100-2400", "2400+"],
        right=True
    )

    # language simplification
    def simplify_lang(lang):
        lang = lang.lower()
        if "python" in lang:              return "Python"
        if "pypy"   in lang:              return "PyPy"
        if "java"   in lang:              return "Java"
        if "c++"    in lang or "g++" in lang: return "C++"
        if "c#"     in lang:              return "C#"
        if "go"     in lang:              return "Go"
        if "rust"   in lang:              return "Rust"
        return "Other"

    df["lang_simple"] = df["language"].apply(simplify_lang)

    return df


def process_contests(raw):
    if len(raw) == 0:
        return pd.DataFrame()

    df = pd.DataFrame(raw)
    df = df.rename(columns={
        "ratingUpdateTimeSeconds": "timestamp",
        "contestName":             "contest",
        "rank":                    "rank",
        "oldRating":               "old_rating",
        "newRating":               "new_rating",
    })

    df["datetime"]    = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    df["date"]        = df["datetime"].dt.date
    df["delta"]       = df["new_rating"] - df["old_rating"]
    df["contest_n"]   = np.arange(1, len(df) + 1)
    df["peak_so_far"] = df["new_rating"].cummax()

    return df


def compute_stats(subs_df, contests_df):
    stats = {}

    if not subs_df.empty:
        ac = subs_df[subs_df["verdict"] == "OK"]
        stats["total_subs"]    = len(subs_df)
        stats["unique_solved"] = ac["prob_name"].nunique()
        stats["ac_rate"]       = round(len(ac) / len(subs_df) * 100, 1)
        rated                  = subs_df["prob_rating"].dropna()
        stats["avg_difficulty"] = int(rated.mean()) if len(rated) else 0
        stats["max_difficulty"] = int(ac["prob_rating"].dropna().max()) if not ac.empty else 0

    if not contests_df.empty:
        stats["contests_played"] = len(contests_df)
        stats["best_rank"]       = int(contests_df["rank"].min())
        stats["max_delta"]       = int(contests_df["delta"].max())

    return stats

def get_weak_topics(subs_df, top_n=5):
    if subs_df.empty:
        return []

    df = subs_df.explode("tags")

    df = df[df["tags"].notna()]

    total = df.groupby("tags").size()

    ac = df[df["verdict"] == "OK"].groupby("tags").size()

    success_rate = (ac / total).fillna(0)

    weak = success_rate.sort_values().head(top_n)

    result = []

    for tag in weak.index:
        result.append({
            "tag": tag,
            "success_rate": round(success_rate[tag] * 100, 1),
            "attempts": int(total[tag])
        })

    return result