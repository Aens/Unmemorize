# coding=utf-8
"""Code by Aens"""
from PySide6 import QtWidgets
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QHeaderView


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
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["Nombre", "Notas", "Fecha de borrado", "Acciones"])
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Adjust the width to others
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Stretch the middle column
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Adjust the width to others
        self.tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Adjust the width to others
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
        # Iterate over the items that we have deleted
        for i, (key, values) in enumerate(self.notepad.deleted_notes.items()):
            name_item = QTableWidgetItem(str(key))
            content_item = QTableWidgetItem(str(values[0]))
            date_item = QTableWidgetItem(str(values[1]))
            # Set the record to the columns
            self.tableWidget.setItem(i, 0, name_item)
            self.tableWidget.setItem(i, 1, content_item)
            self.tableWidget.setItem(i, 2, date_item)
            # Set the buttons to the third column
            delete_button = QPushButton("Borrar")
            delete_button.clicked.connect(lambda name=key: self.delete_forever(key))
            restore_button = QPushButton("Restaurar")
            restore_button.clicked.connect(lambda name=key: self.restore_note(key))
            self.tableWidget.setCellWidget(i, 3, delete_button)
            self.tableWidget.setCellWidget(i, 4, restore_button)

    def delete_forever(self, name: str):
        """Delete a note forever"""
        self.gui.show_in_statusbar(f"ESTE BOTON AUN NO FUNCIONA: Voy a borrar la nota: {name}", mode="error")

    def restore_note(self, name: str):
        """Delete a note forever"""
        self.gui.show_in_statusbar(f"ESTE BOTON AUN NO FUNCIONA: Voy a restaurar la nota: {name}")