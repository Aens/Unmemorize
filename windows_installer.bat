@echo off
setlocal enabledelayedexpansion

echo Installing. Please Wait.
echo Creating virtual environment...

rem Set the virtual environment name
set venv_name=venv
rem Create the virtual environment
python -m venv %venv_name%
rem Activate the virtual environment
call %venv_name%\Scripts\activate

echo Installing python libraries...
rem Install required packages using pip in the virtual environment
pip install -r requirements.txt

echo Disabling virtual environment...
rem Deactivate the virtual environment
deactivate

echo Installation is completed.