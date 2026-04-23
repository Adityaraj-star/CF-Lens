import pytest
import pandas as pd
from src.processor import process_submissions, process_contests, compute_stats


def make_sub(verdict="OK", rating=1200, lang="Python 3", tags=None, ts=1700000000):
    return {
        "id": 1,
        "creationTimeSeconds": ts,
        "verdict": verdict,
        "programmingLanguage": lang,
        "problem": {
            "name": "Test Problem",
            "rating": rating,
            "tags": tags or ["math"],
        }
    }


def make_contest(old=1000, new=1100, ts=1700000000, rank=500):
    return {
        "contestId": 1,
        "contestName": "Round 1",
        "rank": rank,
        "oldRating": old,
        "newRating": new,
        "ratingUpdateTimeSeconds": ts,
    }


# submission tests

def test_empty_submissions():
    df = process_submissions([])
    assert df.empty


def test_basic_columns_present():
    df = process_submissions([make_sub()])
    for col in ["verdict_label", "difficulty_bucket", "lang_simple", "hour", "weekday", "month"]:
        assert col in df.columns


def test_verdict_ok():
    df = process_submissions([make_sub(verdict="OK")])
    assert df["verdict_label"].iloc[0] == "Accepted"


def test_verdict_wa():
    df = process_submissions([make_sub(verdict="WRONG_ANSWER")])
    assert df["verdict_label"].iloc[0] == "Wrong Answer"


def test_verdict_tle():
    df = process_submissions([make_sub(verdict="TIME_LIMIT_EXCEEDED")])
    assert df["verdict_label"].iloc[0] == "TLE"


def test_verdict_re():
    df = process_submissions([make_sub(verdict="RUNTIME_ERROR")])
    assert df["verdict_label"].iloc[0] == "Runtime Error"


def test_verdict_unknown_maps_to_other():
    df = process_submissions([make_sub(verdict="SOME_NEW_THING")])
    assert df["verdict_label"].iloc[0] == "Other"


def test_difficulty_bucket_low():
    df = process_submissions([make_sub(rating=800)])
    assert str(df["difficulty_bucket"].iloc[0]) == "≤900"


def test_difficulty_bucket_high():
    df = process_submissions([make_sub(rating=2500)])
    assert str(df["difficulty_bucket"].iloc[0]) == "2400+"


def test_lang_python():
    df = process_submissions([make_sub(lang="Python 3")])
    assert df["lang_simple"].iloc[0] == "Python"


def test_lang_cpp():
    df = process_submissions([make_sub(lang="GNU G++17 7.3.0")])
    assert df["lang_simple"].iloc[0] == "C++"


def test_missing_rating_handled():
    sub = make_sub()
    sub["problem"].pop("rating")
    df = process_submissions([sub])
    assert pd.isna(df["prob_rating"].iloc[0])


def test_multiple_submissions():
    df = process_submissions([make_sub(), make_sub(verdict="WRONG_ANSWER")])
    assert len(df) == 2


# contest tests

def test_empty_contests():
    df = process_contests([])
    assert df.empty


def test_delta_positive():
    df = process_contests([make_contest(old=1000, new=1100)])
    assert df["delta"].iloc[0] == 100


def test_delta_negative():
    df = process_contests([make_contest(old=1200, new=1150)])
    assert df["delta"].iloc[0] == -50


def test_contest_n_starts_at_one():
    df = process_contests([make_contest()])
    assert df["contest_n"].iloc[0] == 1


def test_contest_n_increments():
    df = process_contests([make_contest(), make_contest()])
    assert df["contest_n"].iloc[1] == 2


def test_peak_so_far_never_decreases():
    contests = [
        make_contest(old=1000, new=1100, ts=1700000000),
        make_contest(old=1100, new=1050, ts=1700100000),
        make_contest(old=1050, new=1200, ts=1700200000),
    ]
    df = process_contests(contests)
    peaks = df["peak_so_far"].values
    assert all(peaks[i] <= peaks[i + 1] for i in range(len(peaks) - 1))


# compute_stats tests

def test_ac_rate_100():
    df = process_submissions([make_sub(verdict="OK")])
    stats = compute_stats(df, pd.DataFrame())
    assert stats["ac_rate"] == 100.0


def test_ac_rate_50():
    df = process_submissions([make_sub(verdict="OK"), make_sub(verdict="WRONG_ANSWER")])
    stats = compute_stats(df, pd.DataFrame())
    assert stats["ac_rate"] == 50.0


def test_best_rank():
    cdf = process_contests([make_contest(rank=500), make_contest(rank=100)])
    stats = compute_stats(pd.DataFrame(), cdf)
    assert stats["best_rank"] == 100