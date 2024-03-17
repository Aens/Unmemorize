# coding=utf-8
"""Code by Aens"""
import pyperclip
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QInputDialog, QLineEdit


class PrivateNotesTab:
    """A Tab to deal with notes, it is expected to handle endless number of notes"""

    def __init__(self, gui):
        """Initialize all the options needed for this tab to work"""
        self.gui = gui  # <-- Pointer to the main GUI
        self.this_tab = self.gui.notes_tab  # <-- Pointer to what holds this tab
        self.settings = self.gui.settings  # <-- Pointer to the settings tab
        # self.private_notes_scroll_layout = None  # <-- Pointer so we can reload this tab later  # TODO FIX
        # Ready to load stuff
        # self.notepad.reload_notes("private")  # Load the notes in memory  # TODO fix this
        self.create_private_notes_tab()  # Create the note tabs populating info from that memory

    ##########
    # LAYOUT #
    ##########

    def create_private_notes_tab(self) -> None:
        """Create the private notes layout and sets it"""
        main_layout = QtWidgets.QVBoxLayout(self.this_tab)
