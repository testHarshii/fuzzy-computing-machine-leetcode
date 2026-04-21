"""
fetch_data.py — Run this script locally whenever you want to update the dashboard.

  1. Edit USERNAMES below with your friends' LeetCode usernames
  2. Run:  python fetch_data.py
  3. It creates data.json in the same folder
  4. Commit & push data.json to GitHub → dashboard updates automatically

Requirements:  pip install requests
"""

import requests
import json
import time
from datetime import datetime

# ─── EDIT THIS LIST ───────────────────────────────────────────
USERNAMES = [
    "harshy03",
    
    # add as many as you want
]
# ──────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
}
URL = "https://leetcode.com/graphql"

QUERY = """
query($username: String!) {
  matchedUser(username: $username) {
    username
    githubUrl
    profile {
      ranking
      userAvatar
      realName
      countryName
      school
      company
      skillTags
    }
    submitStats: submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
        submissions
      }
    }
    userCalendar(year: 2025) {
      streak
      totalActiveDays
      submissionCalendar
    }
    badges {
      displayName
      icon
    }
  }
  allQuestionsCount {
    difficulty
    count
  }
  userContestRanking(username: $username) {
    attendedContestsCount
    rating
    globalRanking
    topPercentage
    badge { name }
  }
}
"""


def fetch_user(username):
    resp = requests.post(
        URL,
        headers=HEADERS,
        json={"query": QUERY, "variables": {"username": username}},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json().get("data", {})

    user = data.get("matchedUser")
    if not user:
        raise ValueError(f"User '{username}' not found")

    ac = user["submitStats"]["acSubmissionNum"]
    aq = data.get("allQuestionsCount", [])
    contest = data.get("userContestRanking") or {}
    calendar = user.get("userCalendar") or {}

    def get(lst, key):
        return next((x["count"] for x in lst if x["difficulty"] == key), 0)

    def get_total(lst, key):
        return next((x["count"] for x in lst if x["difficulty"] == key), 0)

    total_solved = get(ac, "All")
    total_submissions = next((x["submissions"] for x in ac if x["difficulty"] == "All"), 1)
    acceptance = round((total_solved / max(total_submissions, 1)) * 100, 1)

    return {
        "username":        user["username"],
        "realName":        user["profile"].get("realName", ""),
        "avatar":          user["profile"].get("userAvatar", ""),
        "country":         user["profile"].get("countryName", ""),
        "ranking":         user["profile"].get("ranking", 0),
        "totalSolved":     total_solved,
        "easySolved":      get(ac, "Easy"),
        "mediumSolved":    get(ac, "Medium"),
        "hardSolved":      get(ac, "Hard"),
        "totalEasy":       get_total(aq, "Easy"),
        "totalMedium":     get_total(aq, "Medium"),
        "totalHard":       get_total(aq, "Hard"),
        "acceptanceRate":  acceptance,
        "streak":          calendar.get("streak", 0),
        "totalActiveDays": calendar.get("totalActiveDays", 0),
        "contestRating":   round(contest.get("rating", 0)),
        "contestRanking":  contest.get("globalRanking", 0),
        "contestsAttended":contest.get("attendedContestsCount", 0),
        "topPercentage":   contest.get("topPercentage", None),
        "badges":          [b["displayName"] for b in user.get("badges", [])[:3]],
    }


def main():
    results = []
    errors = []

    for i, username in enumerate(USERNAMES):
        print(f"[{i+1}/{len(USERNAMES)}] Fetching {username}...", end=" ", flush=True)
        try:
            data = fetch_user(username)
            results.append(data)
            print(f"✓  {data['totalSolved']} solved")
        except Exception as e:
            errors.append(username)
            print(f"✗  {e}")

        if i < len(USERNAMES) - 1:
            time.sleep(0.8)  # be polite to LeetCode

    output = {
        "updatedAt": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "users": results,
    }

    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✅  Saved {len(results)} users to data.json")
    if errors:
        print(f"⚠   Failed: {', '.join(errors)}")


if __name__ == "__main__":
    main()
