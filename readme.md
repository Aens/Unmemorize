# Installation
* Download python: https://www.python.org/downloads/release/python-3117/
* Run the file `window_installer.bat`

That's it, really.

If the .bat file fails then alternative installation instructions are opening CMD, go to the folder where you want to install it and run:
```
python -m venv venv
venv\Scripts\activate
```
Wait for the Virtual Environment to be enabled and then just install the libraries with:
````
pip install -r requirements.txt
````
Finally, deactivate it and close the window:
```
deactivate
```

# How to Run it
Either run the file: `run.bat` or just while you are on the virtual environment, execute `python Main.py`

# Technologies
This project utilizes the next technologies and libraries:
* Python 3.11 (Programming language)
* PySide6 6.6.1 (Bindings for Python of the C++ Qt framework)
    
