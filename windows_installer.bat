@echo off
setlocal enabledelayedexpansion

rem Set the virtual environment name
set venv_name=venv

rem Create the virtual environment
python -m venv %venv_name%

rem Activate the virtual environment
call %venv_name%\Scripts\activate

rem Install required packages using pip in the virtual environment
pip install -r requirements.txt

rem Deactivate the virtual environment
deactivate

echo Installation is completed.