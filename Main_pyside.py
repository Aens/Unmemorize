# coding=utf-8
"""Code by Alejandro Gutierrez Almansa"""
import sys
from datetime import datetime
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore
import keyboard
from PySide6.QtCore import QCoreApplication
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


class GUI:
    """A GUI to control the notes in an easy to manage interface"""

    def __init__(self, notepad):
        """Initialize the window layout"""
        self.config_file = 'program_settings.ini'
        self.notepad = notepad  # Pointer to our notepad
        self.DEFAULT_WINDOW_SIZE = (800, 600)
        self.DEFAULT_WINDOW_POSITION = (200, 200)
        self.DEFAULT_WINDOW_TRANSPARENCY = 0.8
        self.app = None
        self.window = None

    def load_window_size(self):
        """Load window size from the config file"""
        try:
            settings = QtCore.QSettings(self.config_file, QtCore.QSettings.IniFormat)
            size = settings.value("Window/size", self.DEFAULT_WINDOW_SIZE)
            return size
        except Exception as e:
            print(e)
            return self.DEFAULT_WINDOW_SIZE

    def load_window_config(self):
        """Self-explanatory. It stores the data from a INI file"""
        settings = QtCore.QSettings(self.config_file, QtCore.QSettings.IniFormat)
        size = settings.value("Window/size", self.DEFAULT_WINDOW_SIZE)
        location = settings.value("Window/location", self.DEFAULT_WINDOW_POSITION)
        # Set window size and location
        self.window.resize(size[0], size[1])
        self.window.move(location[0], location[1])

    def save_window_config(self):
        """Self-explanatory. It gets the data from a INI file"""
        settings = QtCore.QSettings(self.config_file, QtCore.QSettings.IniFormat)
        settings.setValue("Window/size", self.window.size())
        settings.setValue("Window/location", self.window.pos())

    def create_window(self):
        """Create the window"""
        if self.app is None:
            self.app = QApplication(sys.argv)
        # Connect the close event signal to the cleanup function
        QCoreApplication.instance().aboutToQuit.connect(self.close_event_handler)
        # First reload the notepad
        self.notepad.reload_notes()
        # Load window size from the config file, set the layout and build the window
        layout = self.build_layout()
        self.window = QtWidgets.QWidget()
        self.window.setWindowTitle(f"Unmemorize {__VERSION__} by {__AUTHOR__}")
        self.window.setLayout(layout)
        self.window.resize(*self.load_window_size())
        self.load_window_config()
        self.window.show()
        # Run the application's event loop
        sys.exit(self.app.exec())

    def event_handler(self):
        """Handle the GUI events"""

    def close_event_handler(self, event):
        """Close event handler"""
        self.save_window_config()  # Store the window size to the config file
        event.accept()

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
        QtWidgets.QMessageBox.information(self.window, "Information", message)


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
def loader():
    """Loader"""
    print(f"{datetime.now()}: Load virtual Notepad.")
    notepad = Notepad()
    print(f"{datetime.now()}: Load GUIs.")
    settings = GUI(notepad=notepad)
    settings.create_window()
    print(f"{datetime.now()}: Load Keybinds.")
    # keys = Keybinds(notepad=notepad, gui=settings)
    # print(f"{datetime.now()}: Start endless loop and wait for commands.")
    # keys.open_settings()
    # keyboard.wait("alt+q")  # TODO activa para continuar
    # print(f"{datetime.now()}: Clean up and close this program.")
    # keys.close_program()


if __name__ == "__main__":
    loader()  # Initialize the program
