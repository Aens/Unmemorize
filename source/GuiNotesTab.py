# coding=utf-8
"""Code by Aens"""
import pyperclip
from datetime import datetime
from PySide6 import QtCore
from PySide6.QtCore import QSize, QPoint
from PySide6.QtGui import QTextCharFormat, QFont
from PySide6.QtWidgets import (QInputDialog, QLineEdit, QDialog, QColorDialog, QGridLayout, QPushButton, QLabel,
                               QScrollArea, QWidget, QTextEdit, QToolBar)


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
        main_layout = QGridLayout(self.this_tab)

        # TOP BUTTONS
        # Add buttons and add them to the layout
        add_note_button = QPushButton('Añadir otra nota')
        add_note_button.clicked.connect(self.add_note)
        deleted_notes_label = QLabel(
            "Las notas borradas no se 'borran', se quedan guardadas en la base de datos "
            "por si acaso borras una importante sin querer.")
        deleted_notes_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # NOTES
        scroll_area = QScrollArea(self.gui)
        scroll_widget = QWidget(scroll_area)
        self.notes_scroll_layout = QGridLayout(scroll_widget)  # <-- pointer to re-populate it
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

    def populate_notes_layout(self, scroll_layout: QGridLayout) -> None:
        """Populates the notes into the layout"""
        row = 0
        col = 0
        for index, (key, value) in enumerate(self.notepad.notes.items()):
            # Add the current note
            note = self.create_note_widget(key, value)
            scroll_layout.addWidget(note, row, col, 1, 1)
            # Choose where to put the next note
            # IF we are in Vertical Endless mode
            if self.settings.NOTES_LAYOUT == 0:  # Vertical
                col += 1
                if col >= self.settings.NOTES_COLUMNS:
                    row += 1
                    col = 0
            # IF we are in Horizontal Endless mode
            elif self.settings.NOTES_LAYOUT == 1:  # Horizontal
                row += 1
                if row >= self.settings.NOTES_ROWS:
                    row = 0
                    col += 1

    def create_note_widget(self, key: str, value: str) -> QWidget:
        """Creates a widget with all the data of a note"""
        # 1: Create the note and its layout
        note = QWidget()
        layout = QGridLayout()

        # 2: Create the elements
        # Create Label
        label = QLabel(f"{key}:")
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)  # Set alignment to right

        # Create TextEdit
        text_edit = QTextEdit()
        text_edit.setHtml(value)
        text_edit.setReadOnly(False)
        # Connect the leaveEvent signal to the save_note method
        text_edit.leaveEvent = lambda event, name=key, obj=text_edit: self.save_note(event="OnLeave", name=name, obj=obj)

        # Create buttons
        button_open = QPushButton("🔍")
        button_copy = QPushButton("📝")
        button_save = QPushButton("💾")
        button_delete = QPushButton("❌")

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
            if isinstance(widget, QTextEdit):
                widget.disconnect(widget)
            widget.deleteLater()
        # Rebuild the layout
        self.populate_notes_layout(self.notes_scroll_layout)

    ###########
    # BUTTONS #
    ###########

    def open_note(self, name: str, obj: QTextEdit) -> None:
        """Copy the note into notepad"""
        new_window = NewWindow(self.gui, notes_tab=self, name=name, text=obj.toHtml())
        new_window.show()
        self.gui.show_in_statusbar(f"Nota '{name}' maximizada.")

    def copy_note(self, name: str, obj: QTextEdit) -> None:
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

    def save_note(self, event: str, name: str, obj: QTextEdit) -> None:
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
        label = QLabel(f"{self.name}:")
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)  # Set alignment to right
        self.text_edit = QTextEdit(self)
        self.text_edit.setHtml(text)
        self.text_edit.leaveEvent = lambda event, name=name, obj=self.text_edit: self.notes_tab.save_note(event="OnLeave", name=name, obj=obj)

        # Create buttons
        button_copy = QPushButton("📝")
        button_save = QPushButton("💾")
        button_delete = QPushButton("❌")
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
        layout = QGridLayout(self)  # <-- pointer to re-populate it
        # Add buttons into the layout (element, row, col, IDK, spans this many columns)
        layout.addWidget(label, 0, 0, 1, 1)
        layout.addWidget(button_copy, 0, 1, 1, 1)
        layout.addWidget(button_save, 0, 2, 1, 1)
        layout.addWidget(button_delete, 0, 3, 1, 1)
        layout.addWidget(self.text_edit, 1, 0, 1, 4)
        self.setLayout(layout)
        # Install an event filter on these new windows
        self.installEventFilter(self)
        # Add Format Editor
        self.add_format_editor()

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

    #################
    # Format Editor #  This section is entirely experimental
    #################

    def add_format_editor(self):
        """Create the Formatting Editor"""
        # Create a toolbar
        toolbar = QToolBar("Formatting Toolbar", self)
        self.layout().addWidget(toolbar)

        # Bold Button
        bold = QPushButton("B", self)
        bold_text = QFont()
        bold_text.setBold(True)
        bold.setFont(bold_text)
        bold.clicked.connect(lambda x: self.format_selection("bold"))
        toolbar.addWidget(bold)

        # Italic Button
        italic = QPushButton("i", self)
        italic_text = QFont()
        italic_text.setItalic(True)
        italic.setFont(italic_text)
        italic.clicked.connect(lambda x: self.format_selection("italic"))
        toolbar.addWidget(italic)

        # Italic Button
        underline = QPushButton("u", self)
        underline_text = QFont()
        underline_text.setUnderline(True)
        underline.setFont(underline_text)
        underline.clicked.connect(lambda x: self.format_selection("underline"))
        toolbar.addWidget(underline)

        # Foreground Color Button
        foreground_color = QPushButton("Color", self)
        foreground_color.setStyleSheet("color: #ff0000;")
        foreground_color.clicked.connect(lambda x: self.format_selection("foreground_color"))
        toolbar.addWidget(foreground_color)

        # Background Color Button
        background_color = QPushButton("Fondo", self)
        background_color.setStyleSheet("background-color: #440000;")
        background_color.clicked.connect(lambda x: self.format_selection("background_color"))
        toolbar.addWidget(background_color)

        # Decrease Font Size Button
        decrease_size = QPushButton("size", self)
        decrease_size.setStyleSheet("font-size: 6pt;")
        decrease_size.clicked.connect(lambda x: self.format_selection("decrease_size"))
        toolbar.addWidget(decrease_size)

        # Increase Font Size Button
        increase_size = QPushButton("size", self)
        increase_size.setStyleSheet("font-size: 12pt;")
        increase_size.clicked.connect(lambda x: self.format_selection("increase_size"))
        toolbar.addWidget(increase_size)

    def format_selection(self, option: str) -> None:
        """Apply a specific format to the current selection"""
        # Create cursor
        cursor = self.text_edit.textCursor()
        # Select text
        selected_text = cursor.selectedText()
        if selected_text:
            # Choose the formatting
            fmt = QTextCharFormat()
            if option == "bold":
                self.toggle_bold(cursor, fmt)
            elif option == "italic":
                self.toggle_italic(cursor, fmt)
            elif option == "underline":
                self.toggle_underline(cursor, fmt)
            elif option == "foreground_color":
                self.set_foreground_to_selection(fmt)
            elif option == "background_color":
                self.set_background_to_selection(fmt)
            elif option == "decrease_size":
                self.decrease_size(fmt)
            elif option == "increase_size":
                self.increase_size(fmt)
            # Apply formatting to the selected text
            if fmt is not None:
                self.text_edit.mergeCurrentCharFormat(fmt)
        else:
            print("No tienes ningún texto seleccionado")

    @staticmethod
    def toggle_bold(cursor, fmt) -> None:
        """Set/Unset Bold formatting to the selected text"""
        fmt.setFontWeight(QFont.Normal if cursor.charFormat().fontWeight() == QFont.Bold else QFont.Bold)

    @staticmethod
    def toggle_italic(cursor, fmt) -> None:
        """Set/Unset Italic formatting to the selected text"""
        fmt.setFontItalic(not cursor.charFormat().fontItalic())

    @staticmethod
    def toggle_underline(cursor, fmt) -> None:
        """Set/Unset Underline formatting to the selected text"""
        fmt.setFontUnderline(not cursor.charFormat().fontUnderline())

    @staticmethod
    def set_foreground_to_selection(fmt) -> None:
        """Set a specific foreground color to the selected text"""
        color = QColorDialog.getColor()
        if color.isValid():
            fmt.setForeground(color)

    @staticmethod
    def set_background_to_selection(fmt) -> None:
        """Set a specific background color to the selected text"""
        color = QColorDialog.getColor()
        if color.isValid():
            fmt.setBackground(color)

    def decrease_size(self, fmt) -> None:
        """Decrease the size of the selected text"""
        current_font = self.text_edit.currentCharFormat().font()
        current_font.setPointSize(current_font.pointSize() - 2)  # Decrement the font size
        fmt.setFont(current_font)

    def increase_size(self, fmt) -> None:
        """Increase the size of the selected text"""
        current_font = self.text_edit.currentCharFormat().font()
        current_font.setPointSize(current_font.pointSize() + 2)  # Increment the font size
        fmt.setFont(current_font)
