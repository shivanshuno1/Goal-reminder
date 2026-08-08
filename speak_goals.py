import sys
import requests
import pyttsx3

API_URL = "https://goal-reminder-zrl3.onrender.com"
TIMEOUT_SECONDS = 45


def fetch_goals():
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
        pass


def speak(goals):
    engine = pyttsx3.init()
    engine.setProperty("rate", 165)

    if not goals:
        engine.say("You have no goals set. Consider adding some.")
    else:
        engine.say(f"Good morning. You have {len(goals)} goals today.")
        for goal in goals:
            engine.say(goal)

    engine.runAndWait()


def main():
    goals = fetch_goals()
    speak(goals)
    if goals:
        mark_read()


if __name__ == "__main__":
    main()
