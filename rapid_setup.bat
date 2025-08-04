@echo off

REM Create virtual environment
echo Creating virtual environment...
python -m venv .venv >>nul 2>&1

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt >>nul 2>&1

REM Display success message
echo Setup complete!
