@echo off
REM Runs speak_goals.py with no console window popping up.
REM Adjust the path to pythonw.exe and the script if needed.

set SCRIPT_DIR=%~dp0
pythonw "%SCRIPT_DIR%speak_goals.py"
