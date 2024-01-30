## Installation
1. Download python: https://www.python.org/downloads/release/python-3117/ (if you are new to python, and you are on windows, just go to the bottom and download the recommended one).
2. Install it (Make sure you checkbox adding it to the PATH, if needed).
3. Download everything on this project and store it in a folder in your PC.
4. Run the file `windows_installer.bat`.

That's it, really.

### Alternative Installation

If the .bat file fails then alternative installation instructions are opening `CMD`, go to the folder where you want to install it and run this to create a virtual environment:
```
python -m venv venv
venv\Scripts\activate
```
Wait for the Virtual Environment to be enabled and then just install the libraries with the next command:
````
pip install -r requirements.txt
````
Finally, deactivate it and close the window:
```
deactivate
```

# How to Run it
* Either run the file: `run.bat`.
* Or just while you are on the virtual environment, execute `python Main.py`

# Technologies
This project utilizes the next technologies and libraries:
* Python 3.11 (Programming language: https://www.python.org)
* PySide6 6.6.1 (Bindings for Python of the C++ Qt framework: https://www.qt.io/qt-for-python)

# Result
![Image](https://github.com/Aens/Unmemorize/blob/master/resources/preview.jpg?raw=true)
