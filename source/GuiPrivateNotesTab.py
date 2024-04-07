# coding=utf-8
"""Code by Aens"""
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QInputDialog, QLineEdit


class PrivateNotesTab:
    """A Tab to deal with notes, it is expected to handle endless number of notes"""

    def __init__(self, gui):
        """Initialize all the options needed for this tab to work"""
        self.gui = gui  # <-- Pointer to the main GUI
        self.this_tab = self.gui.private_notes_tab  # <-- Pointer to what holds this tab
        self.settings = self.gui.settings  # <-- Pointer to the settings tab
        # self.notepad = SQLNotepad(self.gui)  # Pointer to our virtual notepad
        self.private_notes_scroll_layout = None  # <-- Pointer so we can reload this tab later
        # Ready to load stuff
        self.create_private_notes_tab()  # Create the note tabs populating info from that memory

    ##########
    # LAYOUT #
    ##########

    def create_private_notes_tab(self) -> None:
        """Create the private notes layout and sets it"""
