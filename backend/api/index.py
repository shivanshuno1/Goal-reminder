"""
Goal Speaker API (TXT-file backed)
----------------------------------
Stores goals and read logs in a single JSON-formatted .txt file.
No SQLite, no SQLAlchemy — just plain file I/O.

Run locally:
    uvicorn main:app --reload

Deploy on Render:
    Build command: pip install -r requirements.txt
    Start command: uvicorn main:app --host 0.0.0.0 --port $PORT

⚠️  EPHEMERAL STORAGE WARNING (Render free tier):
    The file system resets on every redeploy. For persistence,
    mount a Render Disk or swap to a Postgres DB.
"""

import json
import os
from datetime import date
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ----------------------------------------------------------------------
# File-based storage
# ----------------------------------------------------------------------
DATA_FILE = "goals.txt"  # plain text file, but contains JSON inside


def _read_data():
    """Read the entire data store from the txt file."""
    if not os.path.exists(DATA_FILE):
        # Initialise with empty structure
        return {"goals": [], "read_logs": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # If file is corrupt or empty, reset
        return {"goals": [], "read_logs": []}


def _write_data(data):
    """Write the entire data store to the txt file (as pretty JSON)."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _get_next_id(data):
    """Return the next available goal ID."""
    if not data["goals"]:
        return 1
    return max(g["id"] for g in data["goals"]) + 1


# ----------------------------------------------------------------------
# Pydantic schemas (unchanged)
# ----------------------------------------------------------------------
class GoalCreate(BaseModel):
    text: str


class GoalOut(BaseModel):
    id: int
    text: str
    active: bool

    # Pydantic v2: use `model_config` to enable attribute population
    model_config = {"from_attributes": True}


class StreakOut(BaseModel):
    read_today: bool


# ----------------------------------------------------------------------
# FastAPI app
# ----------------------------------------------------------------------
app = FastAPI(title="Goal Speaker API (TXT backend)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your Vercel domain when live
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------------
# Endpoints
# ----------------------------------------------------------------------
@app.get("/goals", response_model=List[GoalOut])
def list_goals():
    data = _read_data()
    # Return only active goals
    return [g for g in data["goals"] if g["active"]]


@app.post("/goals", response_model=GoalOut)
def create_goal(goal: GoalCreate):
    data = _read_data()
    new_goal = {
        "id": _get_next_id(data),
        "text": goal.text,
        "active": True,
    }
    data["goals"].append(new_goal)
    _write_data(data)
    return new_goal


@app.delete("/goals/{goal_id}")
def delete_goal(goal_id: int):
    data = _read_data()
    for g in data["goals"]:
        if g["id"] == goal_id:
            if not g["active"]:
                raise HTTPException(status_code=404, detail="Goal not found")
            g["active"] = False
            _write_data(data)
            return {"ok": True}
    raise HTTPException(status_code=404, detail="Goal not found")


@app.post("/mark-read", response_model=StreakOut)
def mark_read():
    """Call this after the goals have been spoken aloud today."""
    data = _read_data()
    today = date.today().isoformat()  # "YYYY-MM-DD"

    if today not in data["read_logs"]:
        data["read_logs"].append(today)
        _write_data(data)

    return {"read_today": True}


@app.get("/streak", response_model=StreakOut)
def get_streak():
    data = _read_data()
    today = date.today().isoformat()
    return {"read_today": today in data["read_logs"]}


@app.get("/")
def health():
    return {"status": "ok"}