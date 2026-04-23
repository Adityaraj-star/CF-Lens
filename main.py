import sys
import os

from src.fetcher import fetch_user_info, fetch_submissions, fetch_contest_history
from src.processor import process_submissions, process_contests, get_weak_topics
from src.visualizer import build_dashboard


def main():
    handle = input("Enter Codeforces handle: ").strip()

    if handle == "":
        print("Handle cannot be empty")
        sys.exit()

    print("\nFetching user data...")
    user = fetch_user_info(handle)

    print(f"User: {user['firstName']} {user['lastName']}")
    print(f"Rating: {user.get('rating', 'unrated')} | Rank: {user.get('rank', 'N/A')}")

    print("\nGetting submissions...")
    subs = fetch_submissions(handle)
    print(f"Total submissions fetched: {len(subs)}")

    print("\nGetting contest history...")
    contests = fetch_contest_history(handle)
    print(f"Total contests: {len(contests)}")

    print("\nProcessing data...")
    subs_df = process_submissions(subs)
    weak_topics = get_weak_topics(subs_df)
    contests_df = process_contests(contests)

    print("\nWeak Topics:")

    if not weak_topics:
        print("Not enough data")
    else:
        for t in weak_topics:
            print(f"- {t['tag']} ({t['success_rate']}% success, {t['attempts']} attempts)")

    os.makedirs("output", exist_ok=True)

    output_file = f"output/{handle}_dashboard.png"

    print("\nBuilding dashboard...")
    build_dashboard(subs_df, contests_df, user, output_file)

    print(f"\nDone! Saved at -> {output_file}")


if __name__ == "__main__":
    main()