"""
Goal Speaker API — Postgres-backed (Supabase free tier)
--------------------------------------------------------
Render's free tier has no persistent disk, so goals now live in a
Postgres database (Supabase free tier) instead of a local file. Data
survives service sleeps, restarts, and redeploys.

Environment variable required:
    DATABASE_URL = postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres

Run locally:
    export DATABASE_URL="postgresql://..."
    uvicorn main:app --reload

Deploy on Render:
    Build command: pip install -r requirements.txt
    Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
    Environment variable: DATABASE_URL = your Supabase connection string
"""

import os
from datetime import date
from typing import List

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DATABASE_URL = "postgresql://postgres:[Shivanshu18$]@db.sehwipocynkcnhfvfcno.supabase.co:5432/postgres"

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Add it in Render's Environment tab with your Supabase connection string."
    )


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS goals (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            active BOOLEAN NOT NULL DEFAULT TRUE
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS read_logs (
            read_date DATE PRIMARY KEY
        )
        """
    )
    conn.commit()
    cur.close()
    conn.close()


init_db()


# --- Schemas -------------------------------------------------------------
class GoalCreate(BaseModel):
    text: str


class GoalOut(BaseModel):
    id: int
    text: str
    active: bool


class StreakOut(BaseModel):
    read_today: bool


# --- App -------------------------------------------------------------
app = FastAPI(title="Goal Speaker API (Postgres)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your Vercel domain once deployed
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/goals", response_model=List[GoalOut])
def list_goals():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id, text, active FROM goals WHERE active = TRUE ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.post("/goals", response_model=GoalOut)
def create_goal(goal: GoalCreate):
    text = goal.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Goal text can't be empty")

    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "INSERT INTO goals (text, active) VALUES (%s, TRUE) RETURNING id, text, active",
        (text,),
    )
    new_goal = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return new_goal


@app.delete("/goals/{goal_id}")
def delete_goal(goal_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE goals SET active = FALSE WHERE id = %s AND active = TRUE", (goal_id,))
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Goal not found")
    conn.commit()
    cur.close()
    conn.close()
    return {"ok": True}


@app.post("/mark-read", response_model=StreakOut)
def mark_read():
    today = date.today()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO read_logs (read_date) VALUES (%s) ON CONFLICT DO NOTHING",
        (today,),
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"read_today": True}


@app.get("/streak", response_model=StreakOut)
def get_streak():
    today = date.today()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM read_logs WHERE read_date = %s", (today,))
    found = cur.fetchone() is not None
    cur.close()
    conn.close()
    return {"read_today": found}


@app.get("/")
def health():
    return {"status": "ok"}