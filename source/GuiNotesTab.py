# coding=utf-8
"""Code by Aens"""
import pyperclip
from datetime import datetime
from PySide6 import QtCore
from PySide6.QtCore import QSize, QPoint
from PySide6.QtGui import QTextCharFormat, QFont, QTextListFormat, QTextCursor, QColor, Qt, QIcon
from PySide6.QtWidgets import (QInputDialog, QLineEdit, QDialog, QColorDialog, QGridLayout, QPushButton, QLabel,
                               QScrollArea, QWidget, QTextEdit, QFontComboBox, QStatusBar)
from source.Notepad import SQLNotepad


class NotesTab:
    """A Tab to deal with notes, it is expected to handle endless number of notes"""

    def __init__(self, gui):
        """Initialize all the options needed for this tab to work"""
        self.gui = gui  # <-- Pointer to the main GUI
        self.this_tab = self.gui.notes_tab  # <-- Pointer to what holds this tab
        self.settings = self.gui.settings  # <-- Pointer to the settings tab
        self.notepad = SQLNotepad(self.gui)  # Pointer to our virtual notepad
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

    def delete_note(self, name: str):
        """Delete the note and reload the layout"""
        confirmation = self.gui.ask_for_confirmation(message=f"Seguro que quieres eliminar la nota: {name}")
        if confirmation:
            self.notepad.delete_note(name)
            self.notepad.reload_notes()
            self.reload_notes_layout()
            self.gui.deleted_notes.populate_table()
        else:
            self.gui.show_in_statusbar(f"Nota '{name}' no eliminada. Se ha cancelado el borrado.")

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
        self.text_edit.leaveEvent = (lambda event, _name=name, obj=self.text_edit:  # <-- params
                                     self.notes_tab.save_note(event="OnLeave", name=_name, obj=obj))  # <-- call

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
        button_save.clicked.connect(lambda _name=self.name, obj=self.text_edit:  # <-- params
                                    self.notes_tab.save_note("OnButtonSave", _name, obj))  # <-- call
        button_delete.clicked.connect(self.delete_note_from_here)
        button_copy.clicked.connect(lambda _name=self.name, obj=self.text_edit:  # <-- params
                                    self.notes_tab.copy_note(_name, obj))  # <-- call

        # Create a status bar
        self.statusbar = QStatusBar()
        self.statusbar.setSizeGripEnabled(False)

        # Layout for the new window
        layout = QGridLayout(self)  # <-- pointer to re-populate it
        layout.setColumnStretch(1, 1)
        # Add buttons into the layout (element, row, col, IDK, spans this many columns)
        layout.addWidget(label, 0, 0, 1, 1)
        layout.addWidget(button_copy, 0, 1, 1, 1)
        layout.addWidget(button_save, 0, 2, 1, 1)
        layout.addWidget(button_delete, 0, 3, 1, 1)
        layout.addWidget(self.text_edit, 1, 0, 1, 4)
        # Add the bottom Format Editor
        formatbar_layout = self.add_format_editor(layout)
        layout.addWidget(formatbar_layout, 2, 0, 1, 4)
        # Add the statusbar
        layout.addWidget(self.statusbar, 3, 0, 1, 4)
        self.setLayout(layout)
        # Install an event filter on these new windows
        self.installEventFilter(self)
        # Show a message
        self.show_in_statusbar(message=f"Nota {name} cargada.")

    def show_in_statusbar(self, message: str, mode: str = None) -> None:
        """Show something in the statusbar for a little bit"""
        # Themed modes
        if mode is None:
            self.statusbar.setStyleSheet(self.notes_tab.gui.statusbar_default_themes[self.settings.THEME])
        # Set special modes
        elif mode == "error":
            self.statusbar.setStyleSheet("background-color: darkred; color: white;")
        elif mode == "nothing":
            self.statusbar.setStyleSheet("")
        self.statusbar.showMessage(f"{datetime.now().strftime('%H:%M:%S')} - {message}")

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

    def add_format_editor(self, layout: QGridLayout):
        """Create the Formatting Editor"""
        # Create the layout
        formatbar = QWidget()
        formatbar.setMaximumSize(QSize(900, 70))
        formatbar_layout = QGridLayout(self)
        formatbar.setLayout(formatbar_layout)

        #############
        # Formating #
        #############
        formatting_label = QLabel("Formato")
        formatting_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Bold Button
        bold = QPushButton("B")
        bold.setFixedWidth(25)
        bold_text = QFont()
        bold_text.setBold(True)
        bold.setFont(bold_text)
        bold.clicked.connect(lambda x: self.format_selection("bold"))
        bold.setShortcut("Ctrl+B")

        # Italic Button
        italic = QPushButton("i", self)
        italic.setFixedWidth(25)
        italic_text = QFont()
        italic_text.setItalic(True)
        italic.setFont(italic_text)
        italic.clicked.connect(lambda x: self.format_selection("italic"))
        italic.setShortcut("Ctrl+I")

        # Italic Button
        underline = QPushButton("u", self)
        underline.setFixedWidth(25)
        underline_text = QFont()
        underline_text.setUnderline(True)
        underline.setFont(underline_text)
        underline.clicked.connect(lambda x: self.format_selection("underline"))
        underline.setShortcut("Ctrl+U")

        ########
        # Size #
        ########
        size_label = QLabel("Tamaño")
        size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Decrease Font Size Button
        decrease_size = QPushButton("-", self)
        decrease_size.setFixedWidth(20)
        decrease_size.clicked.connect(lambda x: self.format_selection("decrease_size"))
        decrease_size.setShortcut("Ctrl+-")

        # Increase Font Size Button
        increase_size = QPushButton("+", self)
        increase_size.setFixedWidth(20)
        increase_size.clicked.connect(lambda x: self.format_selection("increase_size"))
        increase_size.setShortcut("Ctrl++")

        ############
        # Coloring #
        ############
        color_label = QLabel("Colorear")
        color_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Background Color Red Button
        background_color_red = QPushButton("", self)
        background_color_red.setIcon(QIcon("resources/icon_red.png"))
        background_color_red.clicked.connect(lambda x: self.format_selection("background_color", QColor(Qt.red)))
        background_color_red.setShortcut("Ctrl+Shift+R")

        # Background Color Green Button
        background_color_green = QPushButton()
        background_color_green.setIcon(QIcon("resources/icon_green.png"))
        background_color_green.clicked.connect(lambda x: self.format_selection("background_color", QColor(Qt.green)))
        background_color_green.setShortcut("Ctrl+Shift+G")

        # Foreground Color Button
        foreground_color = QPushButton()
        foreground_color.setIcon(QIcon("resources/icon_foreground_color.png"))
        foreground_color.clicked.connect(lambda x: self.format_selection("foreground_color"))
        foreground_color.setShortcut("Ctrl+Shift+F")

        # Background Color Button
        background_color = QPushButton()
        background_color.setIcon(QIcon("resources/icon_background_color.png"))
        background_color.clicked.connect(lambda x: self.format_selection("background_color"))
        background_color.setShortcut("Ctrl+Shift+B")

        ###########
        # Cleaner #
        ###########
        clean_label = QLabel("Limpiar")
        clean_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Clean Formats Button
        clean_format = QPushButton()
        clean_format.setIcon(QIcon("resources/icon_clean_format.png"))
        clean_format.clicked.connect(lambda x: self.format_selection("clean_format"))
        clean_format.setShortcut("Ctrl+Shift+C")

        #########
        # Lists #
        #########
        list_label = QLabel("Listas")
        list_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Bullet Lists Button
        bullet_list = QPushButton()
        bullet_list.setIcon(QIcon("resources/icon_bullet_list.png"))
        bullet_list.clicked.connect(lambda x: self.format_selection("bullet_list"))
        bullet_list.setShortcut("Ctrl+L")

        # Decimal Lists Button
        decimal_list = QPushButton()
        decimal_list.setIcon(QIcon("resources/icon_decimal_list.png"))
        decimal_list.clicked.connect(lambda x: self.format_selection("decimal_list"))
        decimal_list.setShortcut("Ctrl+K")

        #############
        # Timestamp #
        #############
        timestamp_label = QLabel("Insertar Fecha y Hora")
        timestamp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Timestamp Date Button
        timestamp = QPushButton()
        timestamp.setIcon(QIcon("resources/icon_date.png"))
        timestamp.clicked.connect(lambda x: self.add_timestamp(mode="date"))
        timestamp.setShortcut("Ctrl+Shift+D")

        # Timestamp Time Button
        timestamp2 = QPushButton()
        timestamp2.setIcon(QIcon("resources/icon_time.png"))
        timestamp2.clicked.connect(lambda x: self.add_timestamp(mode="time"))
        timestamp2.setShortcut("Ctrl+Shift+T")

        # Timestamp Both Button
        timestamp3 = QPushButton()
        timestamp3.setIcon(QIcon("resources/icon_fulltime.png"))
        timestamp3.clicked.connect(lambda x: self.add_timestamp(mode="full"))
        timestamp3.setShortcut("Ctrl+Shift+B")

        #############
        # Font Type #
        #############
        font_label = QLabel("Fuente")
        font_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Font ComboBox
        font_combo = QFontComboBox(self)
        font_combo.currentFontChanged.connect(self.set_font)
        font_combo.setMinimumSize(200, 20)

        # Set the Layout and return it
        # First Row
        formatbar_layout.addWidget(formatting_label, 0, 0, 1, 3)
        formatbar_layout.addWidget(size_label, 0, 4, 1, 2)
        formatbar_layout.addWidget(color_label, 0, 7, 1, 5)
        formatbar_layout.addWidget(clean_label, 0, 12, 1, 1)
        formatbar_layout.addWidget(list_label, 0, 14, 1, 2)
        formatbar_layout.addWidget(timestamp_label, 0, 17, 1, 3)
        formatbar_layout.addWidget(font_label, 0, 21, 1, 1)
        # Second Row
        formatbar_layout.addWidget(bold, 1, 0, 1, 1)
        formatbar_layout.addWidget(italic, 1, 1, 1, 1)
        formatbar_layout.addWidget(underline, 1, 2, 1, 1)
        formatbar_layout.addWidget(self.get_spacer(), 1, 3, 1, 1)
        formatbar_layout.addWidget(decrease_size, 1, 4, 1, 1)
        formatbar_layout.addWidget(increase_size, 1, 5, 1, 1)
        formatbar_layout.addWidget(self.get_spacer(), 1, 6, 1, 1)
        formatbar_layout.addWidget(background_color_red, 1, 7, 1, 1)
        formatbar_layout.addWidget(background_color_green, 1, 8, 1, 1)
        formatbar_layout.addWidget(foreground_color, 1, 9, 1, 1)
        formatbar_layout.addWidget(background_color, 1, 10, 1, 1)
        formatbar_layout.addWidget(self.get_spacer(), 1, 11, 1, 1)
        formatbar_layout.addWidget(clean_format, 1, 12, 1, 1)
        formatbar_layout.addWidget(self.get_spacer(), 1, 13, 1, 1)
        formatbar_layout.addWidget(bullet_list, 1, 14, 1, 1)
        formatbar_layout.addWidget(decimal_list, 1, 15, 1, 1)
        formatbar_layout.addWidget(self.get_spacer(), 1, 16, 1, 1)
        formatbar_layout.addWidget(timestamp, 1, 17, 1, 1)
        formatbar_layout.addWidget(timestamp2, 1, 18, 1, 1)
        formatbar_layout.addWidget(timestamp3, 1, 19, 1, 1)
        formatbar_layout.addWidget(self.get_spacer(), 1, 20, 1, 1)
        formatbar_layout.addWidget(font_combo, 1, 21, 1, 1)
        return formatbar

    @staticmethod
    def get_spacer() -> QWidget:
        """Return a spacer"""
        spacer = QWidget()
        spacer.setFixedSize(10, 20)
        return spacer

    def format_selection(self, option: str, params=None) -> None:
        """Apply a specific format to the current selection"""
        # Create cursor
        cursor = self.text_edit.textCursor()
        # Select text
        selected_text = cursor.selectedText()
        if selected_text:
            # Special formatting that don't use QTextChatFormat or we don't have to Merge with Current Format
            if option == "bullet_list":
                self.toggle_bullet_list(cursor, QTextListFormat.ListDisc)
            elif option == "decimal_list":
                self.toggle_bullet_list(cursor, QTextListFormat.ListDecimal)
            elif option == "clean_format":
                self.clean_format()
            else:
                # Normal formatting options that need a QTextChatFormat
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
                    self.set_background_to_selection(fmt, params)
                elif option == "decrease_size":
                    self.decrease_size(fmt)
                elif option == "increase_size":
                    self.increase_size(fmt)
                # Apply formatting to the selected text
                if fmt is not None:
                    self.text_edit.mergeCurrentCharFormat(fmt)
            self.show_in_statusbar(message=f"Formato {option} aplicado.")
        else:
            self.show_in_statusbar(message="No tienes ningún texto seleccionado.", mode="error")

    @staticmethod
    def toggle_bold(cursor, fmt: QTextCharFormat) -> None:
        """Set/Unset Bold formatting to the selected text"""
        fmt.setFontWeight(QFont.Normal if cursor.charFormat().fontWeight() == QFont.Bold else QFont.Bold)

    @staticmethod
    def toggle_italic(cursor, fmt: QTextCharFormat) -> None:
        """Set/Unset Italic formatting to the selected text"""
        fmt.setFontItalic(not cursor.charFormat().fontItalic())

    @staticmethod
    def toggle_underline(cursor, fmt: QTextCharFormat) -> None:
        """Set/Unset Underline formatting to the selected text"""
        fmt.setFontUnderline(not cursor.charFormat().fontUnderline())

    @staticmethod
    def set_foreground_to_selection(fmt: QTextCharFormat) -> None:
        """Set a specific foreground color to the selected text"""
        color = QColorDialog.getColor()
        if color.isValid():
            fmt.setForeground(color)

    @staticmethod
    def set_background_to_selection(fmt: QTextCharFormat, params: QColor) -> None:
        """Set a specific background color to the selected text"""
        if params is None:
            color = QColorDialog.getColor()
            if color.isValid():
                fmt.setBackground(color)
        else:
            fmt.setBackground(params)

    def decrease_size(self, fmt: QTextCharFormat) -> None:
        """Decrease the size of the selected text"""
        current_font = self.text_edit.currentCharFormat().font()
        current_font.setPointSize(current_font.pointSize() - 2)  # Decrement the font size
        fmt.setFont(current_font)

    def increase_size(self, fmt: QTextCharFormat) -> None:
        """Increase the size of the selected text"""
        current_font = self.text_edit.currentCharFormat().font()
        current_font.setPointSize(current_font.pointSize() + 2)  # Increment the font size
        fmt.setFont(current_font)

    def clean_format(self) -> None:
        """Remove all formatting from the selected text"""
        """Remove all formatting from the selected text"""
        cursor = self.text_edit.textCursor()
        cursor.beginEditBlock()  # Start editing block for undo/redo
        cursor.setPosition(self.text_edit.textCursor().selectionStart())  # Move to the start of the selection
        cursor.setPosition(self.text_edit.textCursor().selectionEnd(), QTextCursor.KeepAnchor)  # Expand the selection
        cursor.setCharFormat(QTextCharFormat())  # Apply an empty format to clear all attributes
        cursor.endEditBlock()  # End editing block

    @staticmethod
    def toggle_bullet_list(cursor, mode: QTextListFormat) -> None:
        """Toggle bullet list formatting for the selected text"""
        # Check if the cursor is positioned inside a list block
        current_list_format = cursor.currentList()
        if current_list_format:
            # Remove list formatting
            block_fmt = cursor.blockFormat()
            block_fmt.setObjectIndex(-1)
            cursor.setBlockFormat(block_fmt)
        else:
            # Apply bullet list formatting
            list_format = QTextListFormat()
            list_format.setStyle(mode)
            cursor.createList(list_format)

    def set_font(self, font):
        """Set a specific font to the selected text. Programmed differently to capture font"""
        # Create cursor
        cursor = self.text_edit.textCursor()
        # Select text
        selected_text = cursor.selectedText()
        if selected_text:
            new_font = QTextCharFormat()
            new_font.setFont(font)
            cursor.mergeCharFormat(new_font)
            self.show_in_statusbar(message=f"Cambio de fuente aplicado.")
        else:
            self.show_in_statusbar(message="No tienes ningún texto seleccionado", mode="error")

    def add_timestamp(self, mode: str) -> None:
        """Adds a timestamp where there is text. Ignore selected text"""
        # Get the current timestamp and format it correctly
        now = datetime.now()
        if mode == "full":
            now = datetime.strftime(now, "%Y-%m-%d %H:%M:%S")
        elif mode == "time":
            now = datetime.strftime(now, "%H:%M:%S")
        elif mode == "date":
            now = datetime.strftime(now, "%Y-%m-%d")
        # Create cursor
        cursor = self.text_edit.textCursor()
        # Make sure we don't have text selected
        selected_text = cursor.selectedText()
        if not selected_text:
            cursor.insertText(now)
            self.show_in_statusbar(message=f"Fecha insertada.")
        else:
            self.show_in_statusbar(message="Tienes texto seleccionado. Para insertar fechas, deseleccionalo", mode="error")
