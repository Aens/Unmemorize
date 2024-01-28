# coding=utf-8
"""Code by Aens"""
import sys
from datetime import datetime
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QSize, QPoint
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QInputDialog, QLineEdit


__VERSION__ = "v0.4"
__AUTHOR__ = "Alex"


class Notepad:
    """A virtual Notepad with all the notes stored"""

    def __init__(self):
        """Load fields from a text file"""
        self.gui = None
        self.notes = {}
        self.folderpath = Path.cwd().joinpath("notes")
        self.deleted_folderpath = Path.cwd().joinpath("old_notes")
        self.reload_notes()

    def add_gui_pointer(self, gui):
        """Add a gui pointer just to call stuff from this class"""
        self.gui = gui

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

    def add_note(self, new_name):
        """Adds a new note"""
        new_note_path = self.folderpath.joinpath(f"{new_name}.txt")
        if new_note_path.exists():
            self.gui.show_popup("Error, esa nota ya existe")
            return
        else:
            try:
                with open(new_note_path, 'w') as file:
                    file.write("")  # Creating an empty note for now
                print(f"Note '{new_name}' added successfully.")
            except Exception as e:
                print(f"Error creating note '{new_name}': {e}")

    def delete_note(self, name: str) -> None:
        """It doesn't delete notes, it just moves them to a different folder"""
        source_filepath = self.folderpath.joinpath(f"{name}.txt")
        destination_filepath = self.deleted_folderpath.joinpath(f"{name}.txt")
        source_filepath.rename(destination_filepath)
        print(f"File moved from {source_filepath} to {destination_filepath}")

    def save_note(self, filename: str, value: str) -> None:
        """Saves a note with this new values"""
        new_note_path = self.folderpath.joinpath(f"{filename}.txt")
        with open(new_note_path, 'w') as file:
            file.write(value)  # Overwriting the content of that note
        print(f"Nota '{filename}' guardada con exito.")


class GUI(QtWidgets.QMainWindow):
    """A GUI to control the notes in an easy to manage interface"""

    def __init__(self, app: QApplication, notepad: Notepad):
        """Initialize the window settings, layour and everything"""
        super().__init__()
        self.app = app
        self.config_file = 'program_settings.ini'
        self.notepad = notepad  # Pointer to our notepad
        self.notepad.add_gui_pointer(self)  # Reverse pointer to our gui
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
        """Creates the layout and sets it"""
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QGridLayout(central_widget)

        add_note_button = QtWidgets.QPushButton('Añadir otra nota')
        add_note_button.clicked.connect(self.add_note)
        deleted_notes_label = QtWidgets.QLabel(
            "Las notas borradas no se 'borran', se almacenan en la carpeta old_notes "
            "por si acaso borras una sin querer.")
        deleted_notes_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        main_layout.addWidget(add_note_button, 0, 0, 1, 1)  # Button in the first row, first column
        main_layout.addWidget(deleted_notes_label, 0, 1, 1, 2)  # Label in the first row, spanning two columns

        scroll_area = QtWidgets.QScrollArea(self)
        scroll_widget = QtWidgets.QWidget(scroll_area)
        scroll_layout = QtWidgets.QGridLayout(scroll_widget)

        row = 0
        col = 0

        for index, (key, value) in enumerate(self.notepad.notes.items()):
            label = QtWidgets.QLabel(f"{key}:")
            label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)  # Set alignment to right
            text_edit = QtWidgets.QTextEdit()
            text_edit.setPlainText(value)
            text_edit.setReadOnly(False)

            # Create buttons
            button_edit = QtWidgets.QPushButton("💾")
            button_delete = QtWidgets.QPushButton("❌")
            button_copy = QtWidgets.QPushButton("📝")

            # Set fixed size for buttons
            button_edit.setFixedSize(30, 30)
            button_copy.setFixedSize(30, 30)
            button_delete.setFixedSize(30, 30)

            # Connect buttons to functions
            button_edit.clicked.connect(lambda name=key, obj=text_edit: self.save_note(name, obj))
            button_delete.clicked.connect(lambda name=key, v=value: self.delete_note(name))
            button_copy.clicked.connect(lambda name=key, obj=text_edit: self.copy_note(obj))

            # Add buttons into the layout (element, row, col, IDK, spans this many columns)
            scroll_layout.addWidget(label, row, col, 1, 1)
            scroll_layout.addWidget(button_edit, row, col + 1, 1, 1)
            scroll_layout.addWidget(button_copy, row, col + 2, 1, 1)
            scroll_layout.addWidget(button_delete, row, col + 3, 1, 1)
            scroll_layout.addWidget(text_edit, row + 1, col, 1, 4)

            row += 2  # Increment by 2 to leave space for buttons

            # Check if we need to start a new column
            if row > 4:
                row = 0
                col += 4  # Increment by 4 to leave space for buttons

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        # Scroll area in the second row, spanning two columns
        # Spanning three columns to avoid bugs
        main_layout.addWidget(scroll_area, 1, 0, 1, 3)

    def reload_layout(self):
        """Reload the layout by destroying it and calling to recreate it"""
        # Clear existing layout
        central_widget = self.centralWidget()
        if central_widget is not None:
            layout = central_widget.layout()
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
        # Rebuild the layout
        self.create_layout()

    @staticmethod
    def copy_note(obj: str) -> None:
        """Copy the note into notepad"""
        pyperclip.copy(obj.toPlainText())

    def delete_note(self, name: str) -> None:
        """Delete the note and reload the layout"""
        self.notepad.delete_note(name)
        self.notepad.reload_notes()
        self.reload_layout()

    def save_note(self, name: str, obj: QtWidgets.QTextEdit) -> None:
        """Save the text on the note and reload the layout"""
        self.notepad.save_note(filename=name, value=obj.toPlainText())
        self.notepad.reload_notes()
        self.reload_layout()

    def add_note(self) -> None:
        """Implements the logic to add a new note"""
        # Capture name of the new file by asking in a popup
        name, ok = QInputDialog.getText(self, "Add Note", "Enter the name for the new note:", QLineEdit.Normal, "")
        if ok and name.strip():
            # Create that file
            self.notepad.add_note(name)
            # Reload notes and layout to also show the new file
            self.notepad.reload_notes()
            self.reload_layout()
        else:
            self.show_popup("Creación de Nota cancelada.")

    def show_popup(self, message: str) -> None:
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
    make_sure_folder_exists(Path.cwd().joinpath("old_notes"))
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
