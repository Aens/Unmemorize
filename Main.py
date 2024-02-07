# coding=utf-8
"""Code by Alejandro Gutierrez Almansa"""
from datetime import datetime
from PySide6.QtWidgets import QApplication
from pathlib import Path
from source import Notepad, Gui
import sys


##########
# LOADER #
##########

MAIN_FOLDER = Path.cwd()


def make_sure_folder_exists(fullpath: Path):
    """Dinamycally create the folder if it doesn't exist."""
    fullpath.mkdir(parents=True, exist_ok=True)


def loader():
    """Loader"""
    make_sure_folder_exists(MAIN_FOLDER.joinpath("notes"))
    print(f"{datetime.now()}: Loading virtual Notepad.")
    notepad = Notepad.Notepad()
    # notepad = Notepad.SQLNotepad()
    print(f"{datetime.now()}: Load GUIs.")
    app = QApplication(sys.argv)
    main_window = Gui.GUI(app=app, notepad=notepad)
    print(f"{datetime.now()}: Running the App.")
    # Run the application's event loop
    main_window.show()
    sys.exit(app.exec())


# Initialize the program
if __name__ == "__main__":
    loader()
