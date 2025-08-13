@echo off
echo Setting up PDF Reader environment...

REM Activate virtual environment
call pdf_reader_env\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

echo Environment setup complete!
echo To activate the environment in the future, run: pdf_reader_env\Scripts\activate
pause
