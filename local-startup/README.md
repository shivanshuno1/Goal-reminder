# Local Startup Speaker

This runs entirely on your PC (no browser) and speaks your goals the
moment you log in, by talking to your deployed Render backend.

## 1. Install dependencies

```
cd local-startup
pip install -r requirements.txt
```

`pyttsx3` uses your OS's built-in TTS engine (SAPI5 on Windows, NSSpeechSynthesizer
on macOS, espeak on Linux) — no internet needed for the speech itself,
just to fetch the goals.

## 2. Configure

Open `speak_goals.py` and set:
```python
API_URL = "https://your-backend.onrender.com"
```
to your actual deployed Render URL.

**Note on Render's free tier:** free web services spin down after
inactivity and take ~30-50 seconds to wake up on the next request. If
your PC calls this right at boot, the first run might time out waiting
for the backend to wake up. Options:
- Bump `TIMEOUT_SECONDS` in the script (e.g. to 60)
- Use Render's paid tier for an always-on instance
- Or just let it retry / fall back to "no goals" gracefully once, then
  work on the second run

## 3. Register it to run at login

### Windows (Task Scheduler)
1. Open **Task Scheduler** → **Create Task** (not "Basic Task", so you get more options)
2. **General tab**: name it "Goal Speaker", check "Run only when user is logged on"
3. **Triggers tab**: New → "At log on" → your user
4. **Actions tab**: New → Action: "Start a program" → Browse to `run_windows.bat`
   (edit that file first if `pythonw` isn't on your PATH — use the full
   path to `pythonw.exe`, usually under `...\Python3x\pythonw.exe`)
5. **Conditions tab**: uncheck "Start the task only if the computer is on AC power" if on a laptop
6. Save. Log off/on to test, or right-click the task → Run.

### macOS (LaunchAgents)
1. Edit `com.goalspeaker.startup.plist`: replace `YOUR_USERNAME` and the
   script path with your actual path.
2. Copy it into place:
   ```
   cp com.goalspeaker.startup.plist ~/Library/LaunchAgents/
   ```
3. Load it:
   ```
   launchctl load ~/Library/LaunchAgents/com.goalspeaker.startup.plist
   ```
4. It'll now run at every login. To test immediately without
   logging out:
   ```
   launchctl start com.goalspeaker.startup
   ```
5. Logs land in `/tmp/goal-speaker.log` and `/tmp/goal-speaker.err` if
   something goes wrong.

To unregister later: `launchctl unload ~/Library/LaunchAgents/com.goalspeaker.startup.plist`

### Linux
Add a `.desktop` file to `~/.config/autostart/` pointing at
`python3 /path/to/speak_goals.py`, or add a `crontab -e` line with
`@reboot`.

## How this differs from the web app

- The web app (Vercel/Render) is what you'd open manually or pin as a
  homepage — good for adding/editing goals with a UI.
- This script is what makes it *actually* speak automatically at
  login, with zero clicks. It reads from the same backend, so goals
  you add in the web UI show up here too.
