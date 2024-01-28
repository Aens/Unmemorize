# coding=utf-8
"""Code by Alejandro Gutierrez Almansa"""
import sys
from datetime import datetime
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QSize, QPoint
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication


__VERSION__ = "v0.3"
__AUTHOR__ = "Aens"


class Notepad:
    """A virtual Notepad with all the notes stored"""

    def __init__(self):
        """Load fields from a text file"""
        self.notes = {}
        self.folderpath = Path.cwd().joinpath("notes")
        self.reload_notes()

    def reload_notes(self):
        """Clean the previous list. Crawl to get all the notes. Load them into the class"""
        self.notes.clear()
        # Load them from files
        files = list(self.folderpath.glob("*.txt"))
        for file in files:
            title = file.stem
            with open(file, encoding="UTF-8") as f:
                content = f.read()
                self.notes[title] = content


class GUI(QtWidgets.QMainWindow):
    """A GUI to control the notes in an easy to manage interface"""

    def __init__(self, app: QApplication, notepad: Notepad):
        """Initialize the window settings, layour and everything"""
        super().__init__()
        self.app = app
        self.config_file = 'program_settings.ini'
        self.notepad = notepad  # Pointer to our notepad
        self.DEFAULT_WINDOW_SIZE = QSize(800, 600)
        self.DEFAULT_WINDOW_POSITION = QPoint(200, 200)
        self.DEFAULT_WINDOW_TRANSPARENCY = 0.8
        self.load_window_config()
        self.setWindowIcon(QIcon(str(Path.cwd().joinpath("MainIcon.png"))))
        self.setWindowTitle(f"Unmemorize {__VERSION__} by {__AUTHOR__}")
        # Install an event filter on the main window
        self.installEventFilter(self)
        # Load the notes in memory
        self.notepad.reload_notes()
        # Finally set the layour
        self.create_layout()

    def load_window_config(self):
        """Self-explanatory. It stores the data from a INI file"""
        settings = QtCore.QSettings(self.config_file, QtCore.QSettings.IniFormat)
        self.resize(settings.value("Window/size", self.DEFAULT_WINDOW_SIZE))
        self.move(settings.value("Window/location", self.DEFAULT_WINDOW_POSITION))

    def save_window_config(self):
        """Self-explanatory. It gets the data from a INI file"""
        settings = QtCore.QSettings(self.config_file, QtCore.QSettings.IniFormat)
        settings.setValue("Window/size", self.size())
        settings.setValue("Window/location", self.pos())

    def eventFilter(self, watched, event):
        """Event filter to handle events on the main window"""
        if watched == self:
            if event.type() == QtCore.QEvent.WindowStateChange:
                if self.isMinimized():
                    print("Window minimized")
            elif event.type() == QtCore.QEvent.Close:
                self.save_window_config()  # Store the window size to the config file
        return super().eventFilter(watched, event)


    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QGridLayout(central_widget)

        add_note_button = QtWidgets.QPushButton('Add Note')
        add_note_button.clicked.connect(self.add_note)
        main_layout.addWidget(add_note_button, 0, 0, 1, 1)  # Button in the first row, first column

        scroll_area = QtWidgets.QScrollArea(self)
        scroll_widget = QtWidgets.QWidget(scroll_area)
        scroll_layout = QtWidgets.QGridLayout(scroll_widget)

        row = 0
        col = 0

        for index, (key, value) in enumerate(self.notepad.notes.items()):
            label_input = QtWidgets.QLineEdit(key)
            text_edit = QtWidgets.QTextEdit()
            text_edit.setPlainText(value)
            text_edit.setReadOnly(True)

            scroll_layout.addWidget(label_input, row, col, 1, 2)  # Span 2 columns for QLineEdit
            scroll_layout.addWidget(text_edit, row + 1, col, 1, 2)  # Start from the row below QLineEdit

            row += 2  # Increment by 2 to leave space for QLineEdit

            # Check if we need to start a new column
            if row > 4:
                row = 0
                col += 2

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        main_layout.addWidget(scroll_area, 1, 0, 1, 2)  # Scroll area in the second row, spanning two columns

    def add_note(self):
        # capture name
        # create file
        # save file
        # reload layout
        pass

    def show_popup(self, message):
        """Show a Pop-up with a message"""
        QtWidgets.QMessageBox.information(self, "Information", message)


##########
# LOADER #
##########

def make_sure_folder_exists(fullpath: Path):
    """Dinamycally create the folder if it doesn't exist."""
    fullpath.mkdir(parents=True, exist_ok=True)


def loader():
    """Loader"""
    make_sure_folder_exists(Path.cwd().joinpath("notes"))
    print(f"{datetime.now()}: Load virtual Notepad.")
    notepad = Notepad()
    print(f"{datetime.now()}: Load GUIs.")
    app = QApplication(sys.argv)
    main_window = GUI(app=app, notepad=notepad)
    # Run the application's event loop
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    loader()  # Initialize the program
