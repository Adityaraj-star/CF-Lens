import pandas as pd


def build_problem_pool(problems_raw):
    rows = []

    for p in problems_raw:
        if "rating" not in p:
            continue

        rows.append({
            "prob_id":    f"{p.get('contestId')}{p.get('index')}",
            "name":       p.get("name"),
            "rating":     p.get("rating"),
            "tags":       p.get("tags", []),
            "contest_id": p.get("contestId"),
            "index":      p.get("index"),
        })

    return pd.DataFrame(rows)


def get_recommendations(weak_topics, problems_df, subs_df, user_rating, per_topic=5, window=(0, 300)):
    if problems_df.empty or not weak_topics:
        return {}

    if not subs_df.empty and "prob_id" in subs_df.columns:
        solved_ids = set(subs_df.loc[subs_df["verdict"] == "OK", "prob_id"])
    else:
        solved_ids = set()

    base_rating = user_rating or 1200
    low = base_rating + window[0]
    high = base_rating + window[1]

    recs = {}

    for wt in weak_topics:
        tag = wt["tag"]

        pool = problems_df[problems_df["tags"].apply(lambda t: tag in t)]
        pool = pool[~pool["prob_id"].isin(solved_ids)]
        pool = pool[(pool["rating"] >= low) & (pool["rating"] <= high)]
        pool = pool.sort_values("rating")

        picks = pool.head(per_topic)

        recs[tag] = [
            {
                "name":   row["name"],
                "rating": int(row["rating"]),
                "url":    f"https://codeforces.com/problemset/problem/{row['contest_id']}/{row['index']}",
            }
            for _, row in picks.iterrows()
        ]

    return recs