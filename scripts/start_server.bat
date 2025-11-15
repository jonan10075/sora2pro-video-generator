@echo off
REM start_server.bat - Launch the Sora2Pro Video Generator server

REM Create virtual environment if it doesn't exist
if not exist venv (
  python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install required Python packages
pip install -r backend\requirements.txt

REM TODO: Replace YOUR_COMET_API_KEY with your actual CometAPI key or set COMET_API_KEY environment variable.
set COMET_API_KEY=YOUR_COMET_API_KEY

REM Run the Flask application
python backend\app.py
