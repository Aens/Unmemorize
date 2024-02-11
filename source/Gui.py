# coding=utf-8
"""Code by Aens"""
from datetime import datetime
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QTabWidget
from source.GuiNotesTab import NotesTab
from source.GuiSettingsTab import SettingsTab


__VERSION__ = "v0.6"
__AUTHOR__ = "Alex"
RESOURCES = Path.cwd().joinpath("resources")


class GUI(QtWidgets.QMainWindow):
    """A GUI to control the notes in an easy to manage interface"""

    def __init__(self, app: QApplication, notepad):
        """Initialize the window settings, layour and everything"""
        super().__init__()
        self.app = app
        self.notepad = notepad  # Pointer to our notepad
        self.notepad.add_gui_pointer(self)  # Reverse pointer to our gui
        self.setWindowIcon(QIcon(str(RESOURCES.joinpath("MainIcon.png"))))
        self.setWindowTitle(f"Unmemorize {__VERSION__} by {__AUTHOR__}")
        self.statusBar = self.statusBar()
        # Create the tabs
        self.tab_widget = QTabWidget(self)
        self.notes_tab = QtWidgets.QWidget(self)
        self.private_notes_tab = QtWidgets.QWidget(self)
        self.settings_tab = QtWidgets.QWidget(self)
        self.tab_widget.addTab(self.notes_tab, "Notas")
        self.tab_widget.addTab(self.private_notes_tab, "Notas Privadas")
        self.tab_widget.addTab(self.settings_tab, "Opciones")
        # Install an event filter on the main window
        self.installEventFilter(self)
        # Create the Content of those tabs
        self.settings = SettingsTab(self)  # <-- Settings must always be loaded before any other tab
        self.notes = NotesTab(self)
        self.create_private_notes_tab()  # TODO TO ITS OWN FILE
        # Set it to the main gui
        self.setCentralWidget(self.tab_widget)

    def show_in_statusbar(self, message: str) -> None:
        """Show something in the statusbar for a little bit"""
        # self.statusBar.setStyleSheet("background-color: darkgreen;")
        self.statusBar.showMessage(f"{datetime.now().strftime('%H:%M:%S')} - {message}")

    def eventFilter(self, watched, event):
        """Event filter to handle events on the main window"""
        if watched == self:
            if event.type() == QtCore.QEvent.WindowStateChange:
                if self.isMinimized():
                    print("Window minimized")
            elif event.type() == QtCore.QEvent.Close:
                self.settings.save_program_config()  # Store the window size to the config file
        return super().eventFilter(watched, event)

    def create_private_notes_tab(self) -> None:
        """Create the private notes tab and set its layout"""
        private_notes_layout = QtWidgets.QVBoxLayout(self.private_notes_tab)

    def show_popup(self, message: str) -> None:
        """Show a Pop-up with a message"""
        QtWidgets.QMessageBox.information(self, "Information", message)
