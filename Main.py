# coding=utf-8
"""Code by Alejandro Gutierrez Almansa"""
from datetime import datetime
from PySide6.QtWidgets import QApplication
from pathlib import Path
from source import Gui
from source.Notepad import PrepareDatabase
import sys

MAIN_FOLDER = Path.cwd()


def loader():
    """Loader"""
    print(f"{datetime.now()}: Checking database integration...")
    make_sure_folder_exists(MAIN_FOLDER.joinpath("notes"))
    PrepareDatabase()
    print(f"{datetime.now()}: Creating GUI...")
    app = QApplication(sys.argv)
    main_window = Gui.GUI(app=app)
    print(f"{datetime.now()}: Executing application endless event loop.")
    main_window.show()
    sys.exit(app.exec())


def make_sure_folder_exists(fullpath: Path):
    """Dinamycally create the folder if it doesn't exist."""
    fullpath.mkdir(parents=True, exist_ok=True)


# Initialize the program
if __name__ == "__main__":
    loader()
