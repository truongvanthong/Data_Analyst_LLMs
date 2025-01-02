@REM Set Up Virtual Environment
python -m venv .venv
@REM Activate Virtual Environment
call .venv\Scripts\activate
@REM Install Required Packages
pip install -r requirements.txt