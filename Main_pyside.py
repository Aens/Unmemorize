# coding=utf-8
"""Code by Alejandro Gutierrez Almansa"""
import sys
from datetime import datetime
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore
import keyboard
from PySide6.QtCore import QSize, QPoint
from PySide6.QtWidgets import QApplication


__VERSION__ = "v0.2"
__AUTHOR__ = "Alex"


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

        # First reload the notepad
        self.notepad.reload_notes()
        # Load window size from the config file, set the layout and build the window
        layout = self.build_layout()
        self.setWindowTitle(f"Unmemorize {__VERSION__} by {__AUTHOR__}")
        self.setLayout(layout)
        self.load_window_config()
        # Install an event filter on the main window
        self.installEventFilter(self)
        self.show()

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
                print("Window closed")
                self.save_window_config()  # Store the window size to the config file
        return super().eventFilter(watched, event)

    def build_layout(self) -> QtWidgets.QVBoxLayout:
        """Build the layout for the APP"""
        layout = QtWidgets.QVBoxLayout()

        add_note_button = QtWidgets.QPushButton('Add Note')
        add_note_button.clicked.connect(self.add_note)
        layout.addWidget(add_note_button)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area_widget = QtWidgets.QWidget()
        scroll_area_layout = QtWidgets.QVBoxLayout()

        for key, value in self.notepad.notes.items():
            label = QtWidgets.QLabel(f"{key}:")
            text_edit = QtWidgets.QTextEdit()
            text_edit.setPlainText(value)
            text_edit.setReadOnly(True)

            scroll_area_layout.addWidget(label)
            scroll_area_layout.addWidget(text_edit)

        scroll_area_widget.setLayout(scroll_area_layout)
        scroll_area.setWidget(scroll_area_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)

        return layout

    def add_note(self):
        # do something
        pass

    def show_popup(self, message):
        """Show a Pop-up with a message"""
        QtWidgets.QMessageBox.information(self, "Information", message)


class Keybinds:
    """Register keybinds to being able to work with this program"""

    def __init__(self, notepad, gui):
        """Register global shortcuts and pointers"""
        self.notepad = notepad
        self.gui = gui
        # keyboard.add_hotkey('alt+d', lambda: PySimpleGUI.popup_get_choice("Choose a field:", fields, title="Select Field"))  # TODO
        keyboard.add_hotkey('alt+d', self.pegar)
        keyboard.add_hotkey('alt+f', self.open_settings)

    def pegar(self):
        """Paste code"""
        print("pego codigo")

    def open_settings(self):
        """Opens the MainMenu Settings Window"""
        print("DEBUG: Abro la GUI")
        self.gui.create_window()

    @staticmethod
    def close_program():
        """Close all the needed things and close the program"""
        keyboard.unhook_all()  # Remove the hotkey to avoid conflicts after the window is closed
        exit()


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
    print(f"{datetime.now()}: Load Keybinds.")
    # keys = Keybinds(notepad=notepad, gui=settings)
    # print(f"{datetime.now()}: Start endless loop and wait for commands.")
    # keys.open_settings()
    # keyboard.wait("alt+q")  # TODO activa para continuar
    # print(f"{datetime.now()}: Clean up and close this program.")
    # keys.close_program()

    # Run the application's event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    loader()  # Initialize the program


 # TODO add a main icon
