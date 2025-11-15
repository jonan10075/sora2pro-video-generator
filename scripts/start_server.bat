@echo off
REM start_server.bat - Launch the Sora2Pro Video Generator server (APIMart)

REM Create virtual environment if it doesn't exist
if not exist venv (
  python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install required Python packages
pip install -r backend\requirements.txt

REM TODO: Replace YOUR_APIMART_API_KEY with your actual APIMart API key or set APIMART_API_KEY environment variable.
set APIMART_API_KEY=YOUR_APIMART_API_KEY

REM Run the Flask application
python backend\app.py
