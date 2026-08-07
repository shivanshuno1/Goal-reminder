import React, { useEffect, useState, useCallback } from "react";

// Set this to your deployed Render backend URL, e.g.
// https://goal-speaker-api.onrender.com
const API_URL = "http://localhost:8000";

interface Goal {
  id: number;
  text: string;
  active: boolean;
}

function speak(text: string) {
  if (!("speechSynthesis" in window)) {
    alert("Speech synthesis isn't supported in this browser.");
    return;
  }
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.95;
  window.speechSynthesis.speak(utterance);
}

export default function App() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [newGoal, setNewGoal] = useState("");
  const [readToday, setReadToday] = useState(false);
  const [hasSpokenThisSession, setHasSpokenThisSession] = useState(false);

  const fetchGoals = useCallback(async () => {
    const res = await fetch(`${API_URL}/goals`);
    const data = await res.json();
    setGoals(data);
  }, []);

  const fetchStreak = useCallback(async () => {
    const res = await fetch(`${API_URL}/streak`);
    const data = await res.json();
    setReadToday(data.read_today);
  }, []);

  useEffect(() => {
    fetchGoals();
    fetchStreak();
  }, [fetchGoals, fetchStreak]);

  const speakGoals = async () => {
    if (goals.length === 0) return;
    const intro = "Here are your goals for today.";
    const combined = [intro, ...goals.map((g) => g.text)].join(". ");
    speak(combined);
    setHasSpokenThisSession(true);

    await fetch(`${API_URL}/mark-read`, { method: "POST" });
    fetchStreak();
  };

  // Many browsers allow speechSynthesis without a user gesture (unlike
  // audio autoplay), so we attempt it automatically on load. If it's
  // blocked, the button below still works.
  useEffect(() => {
    if (goals.length > 0 && !hasSpokenThisSession && !readToday) {
      speakGoals();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [goals]);

  const addGoal = async () => {
    if (!newGoal.trim()) return;
    await fetch(`${API_URL}/goals`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: newGoal.trim() }),
    });
    setNewGoal("");
    fetchGoals();
  };

  const removeGoal = async (id: number) => {
    await fetch(`${API_URL}/goals/${id}`, { method: "DELETE" });
    fetchGoals();
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.h1}>🎯 Goal Speaker</h1>
        <p style={styles.status}>
          {readToday ? "✅ Goals read today" : "🔈 Not read yet today"}
        </p>

        <button style={styles.speakBtn} onClick={speakGoals}>
          Speak my goals
        </button>

        <ul style={styles.list}>
          {goals.map((g) => (
            <li key={g.id} style={styles.listItem}>
              <span>{g.text}</span>
              <button style={styles.removeBtn} onClick={() => removeGoal(g.id)}>
                ✕
              </button>
            </li>
          ))}
        </ul>

        <div style={styles.addRow}>
          <input
            style={styles.input}
            value={newGoal}
            onChange={(e) => setNewGoal(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addGoal()}
            placeholder="Add a new goal…"
          />
          <button style={styles.addBtn} onClick={addGoal}>
            Add
          </button>
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#0f172a",
    fontFamily: "system-ui, sans-serif",
  },
  card: {
    background: "#1e293b",
    padding: "2rem",
    borderRadius: "1rem",
    width: "420px",
    color: "#f1f5f9",
    boxShadow: "0 10px 30px rgba(0,0,0,0.4)",
  },
  h1: { marginTop: 0 },
  status: { color: "#94a3b8", marginBottom: "1rem" },
  speakBtn: {
    width: "100%",
    padding: "0.75rem",
    background: "#6366f1",
    color: "white",
    border: "none",
    borderRadius: "0.5rem",
    fontSize: "1rem",
    cursor: "pointer",
    marginBottom: "1.5rem",
  },
  list: { listStyle: "none", padding: 0, margin: 0 },
  listItem: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "0.5rem 0",
    borderBottom: "1px solid #334155",
  },
  removeBtn: {
    background: "none",
    border: "none",
    color: "#94a3b8",
    cursor: "pointer",
  },
  addRow: { display: "flex", gap: "0.5rem", marginTop: "1rem" },
  input: {
    flex: 1,
    padding: "0.5rem",
    borderRadius: "0.5rem",
    border: "1px solid #334155",
    background: "#0f172a",
    color: "white",
  },
  addBtn: {
    padding: "0.5rem 1rem",
    background: "#334155",
    color: "white",
    border: "none",
    borderRadius: "0.5rem",
    cursor: "pointer",
  },
};
