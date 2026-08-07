# Goal Speaker

Speaks your goals out loud when you open the app, so they stop living
and dying on a sticky note.

## Local dev

**Backend**
```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
Runs at http://localhost:8000

**Frontend**
```
cd frontend
npm install
npm run dev
```
Runs at http://localhost:5173. Create a `.env` file with:
```
VITE_API_URL=http://localhost:8000
```

## Deploy

**Backend → Render**
1. Push `backend/` to a GitHub repo.
2. New Web Service on Render, point at the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Note: free-tier Render disks are ephemeral — the SQLite DB resets on
   redeploy/restart. For real persistence, add a Render Postgres
   instance and swap `DATABASE_URL` in `main.py`.

**Frontend → Vercel**
1. Push `frontend/` to a GitHub repo (or same repo, different root dir).
2. Import into Vercel, set root directory to `frontend`.
3. Add environment variable `VITE_API_URL` = your Render backend URL.
4. Deploy.

## Making it actually run "when you open your PC"

A deployed website can't launch itself on boot — browsers can't do that.
Two ways to get close:

1. **Set it as your browser's homepage / restore-tabs-on-open page**, or
   pin it as the first tab you always open. The app auto-speaks your
   goals as soon as it loads (via `speechSynthesis`), so opening the tab
   is basically all you need to do.
2. **True OS-level auto-launch**: write a small local Python script
   (using `pyttsx3` for offline TTS, or hitting your `/goals` endpoint
   and using the browser) and register it in your OS's startup apps
   (Task Scheduler on Windows, LaunchAgents on macOS). This runs outside
   the browser entirely and is a separate, non-deployed script.

## Streak tracking

`/mark-read` and `/streak` in the backend log whether you've heard your
goals today — a lightweight way to build the "don't skip it" habit the
sticky notes failed at.
