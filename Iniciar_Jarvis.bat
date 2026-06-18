@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
python backend\jarvis_bridge.py
