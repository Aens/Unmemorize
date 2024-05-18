# coding=utf-8
"""Code by Aens"""
from PySide6 import QtWidgets
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QTextBrowser


class DeletedNotesTab:
    """A Tab to deal with deleted notes, it is expected to handle endless number of notes"""

    def __init__(self, gui):
        """Initialize all the options needed for this tab to work"""
        self.gui = gui  # <-- Pointer to the main GUI
        self.this_tab = self.gui.deleted_notes_tab  # <-- Pointer to what holds this tab
        self.settings = self.gui.settings  # <-- Pointer to the settings tab
        self.notepad = self.gui.notes.notepad  # <-- Pointer to the SQL Notepad
        # Create the Table and the tab
        self.tableWidget = QTableWidget()
        self.create_deleted_notes_tab()  # Create the note tabs populating info from that memory

    ##########
    # LAYOUT #
    ##########

    def create_deleted_notes_tab(self) -> None:
        """Create the private notes layout and sets it"""
        layout = QtWidgets.QVBoxLayout(self.this_tab)
        # Create table widget
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["Nombre", "Notas", "Tipo", "Fecha de borrado", "Restaurar", "Borrar"])
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Adjust the width
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Stretch the middle column
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Adjust the width
        self.tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Adjust the width
        self.tableWidget.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Adjust the width
        # Populate tables with data
        self.notepad.reload_deleted_notes()  # Load the notes in memory
        self.populate_table()
        # Add to the layout
        layout.addWidget(self.tableWidget)
        self.this_tab.setLayout(layout)

    def populate_table(self):
        """Populate the table with its content"""
        # Set a fixed amount of rows
        self.notepad.reload_deleted_notes()  # Load the notes in memory
        self.tableWidget.setRowCount(len(self.notepad.deleted_notes))
        self.tableWidget.verticalHeader().setDefaultSectionSize(40)  # Set height to 50 pixels
        # 2 - Iterate over the items that we have deleted
        for i, (_id, values) in enumerate(self.notepad.deleted_notes.items()):
            # 2.1 - Create the items
            name_item = QTableWidgetItem(str(values[0]))
            content_item = QTableWidgetItem()
            text_browser = QTextBrowser()   # SPECIAL: Create a QTextBrowser to render HTML content
            text_browser.setHtml(values[1])
            text_browser.setToolTip(values[1])
            type_item = QTableWidgetItem(str(values[3]))
            date_item = QTableWidgetItem(str(values[2]))
            # 2.2 - Set the record to the columns
            self.tableWidget.setItem(i, 0, name_item)
            self.tableWidget.setItem(i, 1, content_item)
            self.tableWidget.setCellWidget(i, 1, text_browser)
            self.tableWidget.setItem(i, 2, type_item)
            self.tableWidget.setItem(i, 3, date_item)
            # Set the buttons to the third column
            #    We use hackfix as a random param because lambda will CORRUPT the first argument 🙃
            #    so we trick it and use a 2nd one for our only argument
            restore_button = QPushButton("⏪")
            restore_button.clicked.connect(lambda hackfix=None, note_id=_id, name=values[0]:  # <-- Params
                                           self.restore_note(note_id=note_id, name=name))  # <-- Call
            delete_button = QPushButton("❌")
            delete_button.clicked.connect(lambda hackfix=None, note_id=_id, name=values[0]:  # <-- Params
                                          self.delete_forever(note_id=note_id, name=name))  # <-- Call
            # Add buttons to the actual columns
            self.tableWidget.setCellWidget(i, 4, restore_button)
            self.tableWidget.setCellWidget(i, 5, delete_button)

    def delete_forever(self, note_id: int, name: str) -> None:
        """Delete a note forever"""
        confirmation = self.gui.ask_for_confirmation(message=f"¿Borrar PERMANENTEMENTE la nota: {name}?")
        if confirmation:
            self.notepad.delete_note_forever(_id=note_id, name=name)
            self.populate_table()
        else:
            self.gui.show_in_statusbar(f"Nota '{name}' no eliminada. Se ha cancelado el borrado.")

    def restore_note(self, note_id: int, name: str) -> None:
        """Restore a note from the deleted section"""
        self.notepad.restore_note(_id=note_id, name=name)
        self.gui.notes.reload_notes_layout()
        self.gui.private_notes.reload_private_notes_layout()
        self.populate_table()
