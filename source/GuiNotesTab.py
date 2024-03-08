# coding=utf-8
"""Code by Aens"""
import pyperclip
from datetime import datetime
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QSize, QPoint
from PySide6.QtWidgets import QInputDialog, QLineEdit, QDialog


class NotesTab:
    """A Tab to deal with notes, it is expected to handle endless number of notes"""

    def __init__(self, gui):
        """Initialize all the options needed for this tab to work"""
        self.gui = gui  # <-- Pointer to the main GUI
        self.this_tab = self.gui.notes_tab  # <-- Pointer to what holds this tab
        self.settings = self.gui.settings  # <-- Pointer to the settings tab
        self.notepad = self.gui.notepad  # <-- Pointer for lazyness, to not call the gui all the time
        self.notes_scroll_layout = None  # <-- Pointer so we can reload this tab later
        # Ready to load stuff
        self.notepad.reload_notes()  # Load the notes in memory
        self.create_notes_tab()  # Create the note tabs populating info from that memory

    ##########
    # LAYOUT #
    ##########

    def create_notes_tab(self) -> None:
        """Creates the layout and sets it"""
        main_layout = QtWidgets.QGridLayout(self.this_tab)

        # TOP BUTTONS
        # Add buttons and add them to the layout
        add_note_button = QtWidgets.QPushButton('Añadir otra nota')
        add_note_button.clicked.connect(self.add_note)
        deleted_notes_label = QtWidgets.QLabel(
            "Las notas borradas no se 'borran', se quedan guardadas en la base de datos "
            "por si acaso borras una importante sin querer.")
        deleted_notes_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # NOTES
        scroll_area = QtWidgets.QScrollArea(self.gui)
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
        """Populates the notes into the layout"""
        row = 0
        col = 0
        for index, (key, value) in enumerate(self.notepad.notes.items()):
            note = self.create_note_widget(key, value)
            scroll_layout.addWidget(note, row, col, 1, 1)
            # Increment for next note
            row += 1
            # Check if we need to start a new column
            if row >= self.settings.NOTES_ROWS:
                row = 0
                col += 1  # Increment to leave space for buttons. Must be same as wide as the Text_Edit

    def create_note_widget(self, key: str, value: str) -> QtWidgets.QWidget:
        """Creates a widget with all the data of a note"""
        # 1: Create the note and its layout
        note = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()

        # 2: Create the elements
        # Create Label
        label = QtWidgets.QLabel(f"{key}:")
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)  # Set alignment to right

        # Create TextEdit
        text_edit = QtWidgets.QTextEdit()
        text_edit.setHtml(value)
        text_edit.setReadOnly(False)
        # Connect the leaveEvent signal to the save_note method
        text_edit.leaveEvent = lambda event, name=key, obj=text_edit: self.save_note(event="OnLeave", name=name, obj=obj)

        # Create buttons
        button_open = QtWidgets.QPushButton("🔍")
        button_copy = QtWidgets.QPushButton("📝")
        button_save = QtWidgets.QPushButton("💾")
        button_delete = QtWidgets.QPushButton("❌")

        # Set tooltips
        button_open.setToolTip('Abre esta nota en una ventana más grande')
        button_copy.setToolTip('Copia la nota al portapapeles')
        button_save.setToolTip('Guarda la nota de este botón (el resto no serán guardadas)')
        button_delete.setToolTip('Borra la nota de este botón')

        # Set fixed size for buttons
        button_open.setFixedSize(30, 30)
        button_save.setFixedSize(30, 30)
        button_copy.setFixedSize(30, 30)
        button_delete.setFixedSize(30, 30)

        # Connect buttons to functions
        button_open.clicked.connect(lambda name=key, obj=text_edit: self.open_note(name, obj))
        button_save.clicked.connect(lambda name=key, obj=text_edit: self.save_note("OnButtonSave", name, obj))
        button_delete.clicked.connect(lambda name=key, v=value: self.delete_note(name))
        button_copy.clicked.connect(lambda name=key, obj=text_edit: self.copy_note(name, obj))

        # 3: Add elements into the layout.
        # Values mean (element, row, col, row_span, column_span, alignment)
        layout.addWidget(label, 0, 0, 1, 1)
        layout.addWidget(button_open, 0, 1, 1, 1)
        layout.addWidget(button_copy, 0, 2, 1, 1)
        layout.addWidget(button_save, 0, 3, 1, 1)
        layout.addWidget(button_delete, 0, 4, 1, 1)
        layout.addWidget(text_edit, 1, 0, 1, 5)
        # Set the layout for the widget
        note.setLayout(layout)
        return note

    def reload_notes_layout(self) -> None:
        """Reload the layout by destroying it and calling to recreate it"""
        print(f"{datetime.now()}: Reloading notes layout")
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

    ###########
    # BUTTONS #
    ###########

    def open_note(self, name: str, obj: QtWidgets.QTextEdit) -> None:
        """Copy the note into notepad"""
        new_window = NewWindow(self.gui, notes_tab=self, name=name, text=obj.toHtml())
        new_window.show()
        self.gui.show_in_statusbar(f"Nota '{name}' maximizada.")

    def copy_note(self, name: str, obj: QtWidgets.QTextEdit) -> None:
        """Copy the note into notepad"""
        pyperclip.copy(obj.toPlainText())
        self.gui.show_in_statusbar(f"Nota '{name}' copiada al portapapeles.")

    def delete_note(self, name: str) -> bool:
        """Delete the note and reload the layout"""
        if confirmation := self.gui.ask_for_confirmation(message=f"Seguro que quieres eliminar la nota llamada: {name}"):
            self.notepad.delete_note(name)
            self.notepad.reload_notes()
            self.reload_notes_layout()
        else:
            self.gui.show_in_statusbar(f"Nota '{name}' no eliminada. Se ha cancelado el borrado.")
        return confirmation

    def save_note(self, event: str, name: str, obj: QtWidgets.QTextEdit) -> None:
        """Save the text on the note and reload the layout"""
        # Capture Events to make sure we only save on specific conditions
        if event == "OnLeave":
            if not self.settings.AUTOSAVE:
                return  # DON'T save on Leave Events if autosave is not ON.
        elif event == "OnButtonSave":
            pass
        # Check if the note for what we triggered the event requires an actual save or nothing changed
        # This is a huge efficiency trick, we don't want thosands of unnecesary reloads on the GUI
        value = obj.toHtml()
        if value == self.notepad.notes[name]:
            return   # DON'T save as it's not needed
        # If we made it this far, okay, go ahead and save the note
        self.notepad.save_note(filename=name, value=value)
        self.notepad.reload_notes()
        self.reload_notes_layout()

    def add_note(self) -> None:
        """Implements the logic to add a new note"""
        # Capture name of the new file by asking in a popup
        name, ok = QInputDialog.getText(self.gui, "Add Note", "Enter the name for the new note:", QLineEdit.Normal, "")
        if ok and name.strip():
            # Create that file
            self.notepad.add_note(name)
            # Reload notes and layout to also show the new file
            self.notepad.reload_notes()
            self.reload_notes_layout()
        else:
            self.gui.show_popup("Creación de Nota cancelada.")


class NewWindow(QDialog):
    """Creates the new big window"""
    def __init__(self, parent=None, notes_tab=None, name=None, text: str = ""):
        super().__init__(parent)
        # New window setup
        self.setGeometry(200, 200, 400, 300)
        self.notes_tab = notes_tab
        self.settings = self.notes_tab.settings
        self.name = name
        self.setWindowTitle(f"Nota: {name}")
        self.load_window_config()

        # Create TextEdit and Labels
        label = QtWidgets.QLabel(f"{self.name}:")
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)  # Set alignment to right
        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setHtml(text)
        self.text_edit.leaveEvent = lambda event, name=name, obj=self.text_edit: self.notes_tab.save_note(event="OnLeave", name=name, obj=obj)

        # Create buttons
        button_copy = QtWidgets.QPushButton("📝")
        button_save = QtWidgets.QPushButton("💾")
        button_delete = QtWidgets.QPushButton("❌")
        # Set tooltips
        button_copy.setToolTip('Copia la nota al portapapeles')
        button_save.setToolTip('Guarda la nota de este botón (el resto no serán guardadas)')
        button_delete.setToolTip('Borra la nota de este botón')
        # Set fixed size for buttons
        button_save.setFixedSize(30, 30)
        button_copy.setFixedSize(30, 30)
        button_delete.setFixedSize(30, 30)
        # Connect buttons to functions
        button_save.clicked.connect(lambda name=self.name, obj=self.text_edit: self.notes_tab.save_note("OnButtonSave", name, obj))
        button_delete.clicked.connect(self.delete_note_from_here)
        button_copy.clicked.connect(lambda name=self.name, obj=self.text_edit: self.notes_tab.copy_note(name, obj))

        # Layout for the new window
        layout = QtWidgets.QGridLayout(self)  # <-- pointer to re-populate it
        # Add buttons into the layout (element, row, col, IDK, spans this many columns)
        layout.addWidget(label, 0, 0, 1, 1)
        layout.addWidget(button_copy, 0, 1, 1, 1)
        layout.addWidget(button_save, 0, 2, 1, 1)
        layout.addWidget(button_delete, 0, 3, 1, 1)
        layout.addWidget(self.text_edit, 1, 0, 1, 4)
        self.setLayout(layout)
        # Install an event filter on these new windows
        self.installEventFilter(self)

    def delete_note_from_here(self):
        """Just close the window after deleting the note"""
        confirmation = self.notes_tab.delete_note(self.name)
        if confirmation:
            self.close()

    def eventFilter(self, watched, event):
        """Event filter to handle events on the main window"""
        if watched == self:
            if event.type() == QtCore.QEvent.Close:
                self.save_window_config()  # Store the window size to the config file
        return super().eventFilter(watched, event)

    def load_window_config(self) -> None:
        """Self-explanatory. It stores the data from a INI file"""
        # Try to find the settings or just load the default values
        self.resize(self.settings.settings_file.value("Subwindows/notes_size", QSize(800, 600)))
        self.move(self.settings.settings_file.value("Subwindows/notes_location", QPoint(200, 200)))

    def save_window_config(self) -> None:
        """Save the window size to the config file"""
        self.settings.settings_file.setValue("Subwindows/notes_size", self.size())
        self.settings.settings_file.setValue("Subwindows/notes_location", self.pos())
