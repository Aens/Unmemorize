# coding=utf-8
"""Code by Aens"""
from datetime import datetime
import pyperclip
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QSize, QPoint
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QInputDialog, QLineEdit, QTabWidget


__VERSION__ = "v0.6"
__AUTHOR__ = "Alex"
RESOURCES = Path.cwd().joinpath("resources")
SETTINGS = 'program_settings.ini'


class GUI(QtWidgets.QMainWindow):
    """A GUI to control the notes in an easy to manage interface"""

    def __init__(self, app: QApplication, notepad):
        """Initialize the window settings, layour and everything"""
        super().__init__()
        self.app = app
        self.settings = QtCore.QSettings(SETTINGS, QtCore.QSettings.IniFormat)
        self.notepad = notepad  # Pointer to our notepad
        self.notepad.add_gui_pointer(self)  # Reverse pointer to our gui
        self.setWindowIcon(QIcon(str(RESOURCES.joinpath("MainIcon.png"))))
        self.setWindowTitle(f"Unmemorize {__VERSION__} by {__AUTHOR__}")
        self.statusBar = self.statusBar()
        # Settings
        self.AUTOSAVE = False
        self.THEME = 0
        self.load_program_config()  # Override default settings with the ones from file
        # Install an event filter on the main window
        self.installEventFilter(self)
        # Create the tabs
        self.tab_widget = QTabWidget(self)
        self.notes_tab = QtWidgets.QWidget(self)
        self.notes_scroll_layout = None  # <-- Pointer so we can reload it later
        self.private_notes_tab = QtWidgets.QWidget(self)
        self.settings_tab = QtWidgets.QWidget(self)
        self.tab_widget.addTab(self.notes_tab, "Notas")
        self.tab_widget.addTab(self.private_notes_tab, "Notas Privadas")
        self.tab_widget.addTab(self.settings_tab, "Opciones")

        # Initialize the content of those tabs
        self.create_notes_tab()
        self.create_private_notes_tab()
        self.create_settings_tab()
        self.setCentralWidget(self.tab_widget)
        # Load the notes in memory
        self.notepad.reload_notes()

    def show_in_statusbar(self, message: str) -> None:
        """Show something in the statusbar for a little bit"""
        # self.statusBar.setStyleSheet("background-color: darkgreen;")
        self.statusBar.showMessage(f"{datetime.now().strftime('%H:%M:%S')} - {message}")

    def load_program_config(self) -> None:
        """Self-explanatory. It stores the data from a INI file"""
        self.setWindowOpacity(1)
        # Try to find the settings or just load the default values
        self.resize(self.settings.value("Window/size", QSize(800, 600)))
        self.move(self.settings.value("Window/location", QPoint(200, 200)))
        self.AUTOSAVE = True if self.settings.value("Settings/autosave_notes", "false") == "true" else False
        self.THEME = self.settings.value("Settings/theme", 0)
        self.change_stylesheet(self.THEME)

    def save_program_config(self) -> None:
        """Self-explanatory. It gets the data from a INI file"""
        self.settings.setValue("Window/size", self.size())
        self.settings.setValue("Window/location", self.pos())
        self.settings.setValue("Settings/autosave_notes", self.AUTOSAVE)
        self.settings.setValue("Settings/theme", self.THEME)

    def eventFilter(self, watched, event):
        """Event filter to handle events on the main window"""
        if watched == self:
            if event.type() == QtCore.QEvent.WindowStateChange:
                if self.isMinimized():
                    print("Window minimized")
            elif event.type() == QtCore.QEvent.Close:
                self.save_program_config()  # Store the window size to the config file
        return super().eventFilter(watched, event)

##########
# LAYOUT #
##########

    def create_private_notes_tab(self) -> None:
        """Create the private notes tab and set its layout"""
        private_notes_layout = QtWidgets.QVBoxLayout(self.private_notes_tab)

    def create_notes_tab(self) -> None:
        """Creates the layout and sets it"""
        main_layout = QtWidgets.QGridLayout(self.notes_tab)

        # TOP BUTTONS
        # Add buttons and add them to the layout
        add_note_button = QtWidgets.QPushButton('Añadir otra nota')
        add_note_button.clicked.connect(self.add_note)
        deleted_notes_label = QtWidgets.QLabel(
            "Las notas borradas no se 'borran', se quedan guardadas en la base de datos "
            "por si acaso borras una importante sin querer.")
        deleted_notes_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # NOTES
        scroll_area = QtWidgets.QScrollArea(self)
        scroll_widget = QtWidgets.QWidget(scroll_area)
        self.notes_scroll_layout = QtWidgets.QGridLayout(scroll_widget)  # <-- pointer to re-populate it
        scroll_widget.setProperty("notesContainer", True)
        # Build and populate the layout with arbitrary notes
        self.populate_notes_layout(self.notes_scroll_layout)

        # Add all elements to the current layout
        main_layout.addWidget(add_note_button, 0, 0, 1, 1)  # Add button in the first row, first column
        main_layout.addWidget(deleted_notes_label, 0, 1, 1, 2)  # Add label in the first row, spanning two columns
        scroll_widget.setLayout(self.notes_scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area, 1, 0, 1, 3)

    def populate_notes_layout(self, scroll_layout: QtWidgets.QGridLayout) -> None:
        """Populates the notes layout"""
        row = 0
        col = 0
        for index, (key, value) in enumerate(self.notepad.notes.items()):
            label = QtWidgets.QLabel(f"{key}:")
            label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)  # Set alignment to right

            # Create TextEdits
            text_edit = QtWidgets.QTextEdit()
            text_edit.setPlainText(value)
            text_edit.setReadOnly(False)
            # Connect the leaveEvent signal to the save_note method
            text_edit.leaveEvent = lambda event, name=key, obj=text_edit: self.save_note(event="OnLeave", name=name, obj=obj)

            # Create buttons
            button_save = QtWidgets.QPushButton("💾")
            button_delete = QtWidgets.QPushButton("❌")
            button_copy = QtWidgets.QPushButton("📝")

            # Set fixed size for buttons
            button_save.setFixedSize(30, 30)
            button_copy.setFixedSize(30, 30)
            button_delete.setFixedSize(30, 30)

            # Connect buttons to functions
            button_save.clicked.connect(lambda name=key, obj=text_edit: self.save_note("OnButtonSave", name, obj))
            button_delete.clicked.connect(lambda name=key, v=value: self.delete_note(name))
            button_copy.clicked.connect(lambda name=key, obj=text_edit: self.copy_note(name, obj))

            # Add buttons into the layout (element, row, col, IDK, spans this many columns)
            scroll_layout.addWidget(label, row, col, 1, 1)
            scroll_layout.addWidget(button_save, row, col + 1, 1, 1)
            scroll_layout.addWidget(button_copy, row, col + 2, 1, 1)
            scroll_layout.addWidget(button_delete, row, col + 3, 1, 1)
            scroll_layout.addWidget(text_edit, row + 1, col, 1, 4)

            row += 2  # Increment by 2 to leave space for buttons
            if row > 4:  # Check if we need to start a new column
                row = 0
                col += 4  # Increment by 4 to leave space for buttons

############
# Settings #
############

    def create_settings_tab(self) -> None:
        """Create the settings tab and set its layout"""
        # 1 - Stylesheets
        stylesheet_label = QtWidgets.QLabel("Estilo del programa:")
        stylesheet_combobox = QtWidgets.QComboBox()
        stylesheet_combobox.addItem("Gris")
        stylesheet_combobox.addItem("Oscuro")
        stylesheet_combobox.addItem("Azul")
        stylesheet_combobox.addItem("Verde")
        # 2 - AutoSave
        auto_save_checkbox = QtWidgets.QCheckBox("Guardar Notas Automáticamente")
        auto_save_checkbox.setChecked(self.AUTOSAVE)  # Set the initial state
        # Set up a grid layout for the label and combobox
        settings_layout = QtWidgets.QGridLayout(self.settings_tab)
        settings_layout.addWidget(stylesheet_label, 0, 0)  # Label in the first row, first column
        settings_layout.addWidget(stylesheet_combobox, 0, 1)  # Combobox in the first row, second column
        settings_layout.addWidget(auto_save_checkbox, 1, 0, 1, 2)  # Combobox in the first row, second column
        settings_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)  # Align to top-left

        # Connections/Events
        stylesheet_combobox.currentIndexChanged.connect(self.change_stylesheet)
        auto_save_checkbox.stateChanged.connect(self.handle_auto_save_checkbox)

    def handle_auto_save_checkbox(self, state: int) -> None:
        """Disable or enable the auto-saving
           :param state: values can be 0 or 2"""
        if state:
            self.AUTOSAVE = True
        else:
            self.AUTOSAVE = False

    def change_stylesheet(self, style: int) -> None:
        """Change the application stylesheet"""
        style = str(style)
        mapped_options = {
            "0": "resources/theme_gray.QSS",
            "1": "resources/theme_dark.QSS",
            "2": "resources/theme_light.QSS",
            "3": "resources/theme_green.QSS"
        }
        with open(mapped_options[style], "r", encoding="UTF-8") as file:
            stylesheet = file.read()
        self.THEME = style
        self.app.setStyleSheet(stylesheet)

    #########
    # Notes #
    #########

    def reload_notes_layout(self) -> None:
        """Reload the layout by destroying it and calling to recreate it"""
        # Delete existing layout if it does exist
        for i in reversed(range(self.notes_scroll_layout.count())):
            item = self.notes_scroll_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, QtWidgets.QTextEdit):
                widget.disconnect(widget)
            widget.deleteLater()
            # widget.setParent(None)  # TODO for some reason this duplicates the onLeave events
        # Rebuild the layout
        self.populate_notes_layout(self.notes_scroll_layout)

    def copy_note(self, name: str, obj: str) -> None:
        """Copy the note into notepad"""
        pyperclip.copy(obj.toPlainText())
        self.show_in_statusbar(f"Nota '{name}' copiada al portapapeles.")

    def delete_note(self, name: str) -> None:
        """Delete the note and reload the layout"""
        self.notepad.delete_note(name)
        self.notepad.reload_notes()
        self.reload_notes_layout()

    def save_note(self, event: str, name: str, obj: QtWidgets.QTextEdit) -> None:
        """Save the text on the note and reload the layout"""
        # Capture Events to make sure we only save on specific conditions
        if event == "OnLeave":
            if not self.AUTOSAVE:
                return  # DON'T save on Leave Events if autosave is not ON.
        elif event == "OnButtonSave":
            pass
        # Check if the note for what we triggered the event requires an actual save or nothing changed
        # This is a huge efficiency trick, we don't want thosands of unnecesary reloads on the GUI
        value = obj.toPlainText()
        if value == self.notepad.notes[name]:
            return   # DON'T save as it's not needed
        # If we made it this far, okay, go ahead and save the note
        self.notepad.save_note(filename=name, value=value)
        self.notepad.reload_notes()
        self.reload_notes_layout()

    def add_note(self) -> None:
        """Implements the logic to add a new note"""
        # Capture name of the new file by asking in a popup
        name, ok = QInputDialog.getText(self, "Add Note", "Enter the name for the new note:", QLineEdit.Normal, "")
        if ok and name.strip():
            # Create that file
            self.notepad.add_note(name)
            # Reload notes and layout to also show the new file
            self.notepad.reload_notes()
            self.reload_notes_layout()
        else:
            self.show_popup("Creación de Nota cancelada.")

    def show_popup(self, message: str) -> None:
        """Show a Pop-up with a message"""
        QtWidgets.QMessageBox.information(self, "Information", message)

