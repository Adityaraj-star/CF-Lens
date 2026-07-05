import pandas as pd
from src.recommender import build_problem_pool, get_recommendations


def make_problem(contest_id=1, index="A", rating=1200, tags=None):
    return {
        "contestId": contest_id,
        "index": index,
        "name": f"Problem {index}",
        "rating": rating,
        "tags": tags or ["math"],
    }


def test_build_problem_pool_skips_unrated():
    raw = [make_problem(rating=1200), {"contestId": 2, "index": "B", "name": "No rating"}]
    df = build_problem_pool(raw)
    assert len(df) == 1


def test_recommendations_respect_rating_window():
    problems_df = build_problem_pool([
        make_problem(index="A", rating=1200, tags=["dp"]),
        make_problem(index="B", rating=2000, tags=["dp"]),
    ])
    weak_topics = [{"tag": "dp", "success_rate": 10.0, "attempts": 5}]
    recs = get_recommendations(weak_topics, problems_df, pd.DataFrame(), user_rating=1200, window=(0, 300))
    names = [p["name"] for p in recs["dp"]]
    assert "Problem A" in names
    assert "Problem B" not in names


def test_recommendations_exclude_solved():
    problems_df = build_problem_pool([make_problem(contest_id=1, index="A", rating=1200, tags=["dp"])])
    subs_df = pd.DataFrame([{"prob_id": "1A", "verdict": "OK"}])
    weak_topics = [{"tag": "dp", "success_rate": 10.0, "attempts": 5}]
    recs = get_recommendations(weak_topics, problems_df, subs_df, user_rating=1200)
    assert recs["dp"] == []


def test_empty_weak_topics_returns_empty():
    recs = get_recommendations([], pd.DataFrame({"tags": [["dp"]]}), pd.DataFrame(), 1200)
    assert recs == {}