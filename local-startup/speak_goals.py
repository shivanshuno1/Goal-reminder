"""
speak_goals.py
--------------
Runs on PC startup. Fetches your goals from the deployed backend
and speaks them aloud offline (no browser needed).

Setup:
    pip install pyttsx3 requests

Config:
    Set API_URL below to your deployed Render backend, e.g.
    https://goal-speaker-api.onrender.com

Then register this script to run at login (see README section below).
"""

import sys
import requests
import pyttsx3

API_URL = "http://localhost:8000"  # Default for local testing — change to deployed URL when deploying
TIMEOUT_SECONDS = 10


def fetch_goals() -> list[str]:
    try:
        res = requests.get(f"{API_URL}/goals", timeout=TIMEOUT_SECONDS)
        res.raise_for_status()
        goals = res.json()
        return [g["text"] for g in goals]
    except requests.RequestException as e:
        print(f"Could not reach backend: {e}", file=sys.stderr)
        return []


def mark_read():
    try:
        requests.post(f"{API_URL}/mark-read", timeout=TIMEOUT_SECONDS)
    except requests.RequestException:
        pass  # non-critical, don't block speech on this


def speak(lines: list[str]):
    engine = pyttsx3.init()
    engine.setProperty("rate", 165)  # words per minute, adjust to taste

    if not lines:
        engine.say("You have no goals set. Consider adding some.")
    else:
        engine.say("Good morning. Here are your goals for today.")
        for line in lines:
            engine.say(line)

    engine.runAndWait()


def main():
    goals = fetch_goals()
    speak(goals)
    if goals:
        mark_read()


if __name__ == "__main__":
    main()
