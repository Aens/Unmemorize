# coding=utf-8
"""Code by Aens"""
import pyperclip
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QInputDialog, QLineEdit


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

    ###########
    # BUTTONS #
    ###########

    def copy_note(self, name: str, obj: str) -> None:
        """Copy the note into notepad"""
        pyperclip.copy(obj.toPlainText())
        self.gui.show_in_statusbar(f"Nota '{name}' copiada al portapapeles.")

    def delete_note(self, name: str) -> None:
        """Delete the note and reload the layout"""
        self.notepad.delete_note(name)
        self.notepad.reload_notes()
        self.reload_notes_layout()

    def save_note(self, event: str, name: str, obj: QtWidgets.QTextEdit) -> None:
        """Save the text on the note and reload the layout"""
        # Capture Events to make sure we only save on specific conditions
        if event == "OnLeave":
            if not self.settings.AUTOSAVE:  # TODO fix this when settings tab works
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
        name, ok = QInputDialog.getText(self.gui, "Add Note", "Enter the name for the new note:", QLineEdit.Normal, "")
        if ok and name.strip():
            # Create that file
            self.notepad.add_note(name)
            # Reload notes and layout to also show the new file
            self.notepad.reload_notes()
            self.reload_notes_layout()
        else:
            self.gui.show_popup("Creación de Nota cancelada.")
