# coding=utf-8
"""Code by Aens"""
from datetime import datetime
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QTabWidget
from source.GuiNotesTab import NotesTab
from source.GuiNotesDeletedTab import DeletedNotesTab
from source.GuiPrivateNotesTab import PrivateNotesTab
from source.GuiSettingsTab import SettingsTab

__VERSION__ = "v0.9"
__AUTHOR__ = "Alex"
RESOURCES = Path.cwd().joinpath("resources")


class GUI(QtWidgets.QMainWindow):
    """A GUI to control the notes in an easy to manage interface"""

    def __init__(self, app: QApplication):
        """Initialize the window settings, layour and everything"""
        super().__init__()
        self.app = app
        self.setWindowIcon(QIcon(str(RESOURCES.joinpath("MainIcon.png"))))
        self.setWindowTitle(f"Unmemorize {__VERSION__} by {__AUTHOR__}")
        # Statusbar
        self.statusbar_default_themes = {
                0: "background-color: #E9E9E9; color: black;",  # Gray theme
                1: "background-color: #46494F; color: white;",  # Dark theme
                2: "background-color: #A6D8FF; color: black;",  # Blue theme
                3: "background-color: #58886B; color: black;"}  # Green theme
        self.statusBar = self.statusBar()
        # Create the tabs
        self.tab_widget = QTabWidget(self)
        self.notes_tab = QtWidgets.QWidget(self)
        self.private_notes_tab = QtWidgets.QWidget(self)
        self.deleted_notes_tab = QtWidgets.QWidget(self)
        self.tasks_tab = QtWidgets.QWidget(self)
        self.settings_tab = QtWidgets.QWidget(self)
        self.tab_widget.addTab(self.notes_tab, "Notas")
        self.tab_widget.addTab(self.private_notes_tab, "Notas Privadas")
        self.tab_widget.addTab(self.deleted_notes_tab, "Notas Borradas")
        self.tab_widget.addTab(self.tasks_tab, "Lista de Tareas")
        self.tab_widget.addTab(self.settings_tab, "Opciones")
        # Install an event filter on the main window
        self.installEventFilter(self)
        # Create the Content of those tabs
        self.settings = SettingsTab(self)  # <-- Settings must always be loaded before any other tab
        self.notes = NotesTab(self)
        self.deleted_notes = DeletedNotesTab(self)
        self.private_notes = PrivateNotesTab(self)
        # Set it to the main gui
        self.setCentralWidget(self.tab_widget)
        self.show_in_statusbar("Programa Listo")

    def eventFilter(self, watched, event):
        """Event filter to handle events on the main window"""
        if watched == self:
            if event.type() == QtCore.QEvent.WindowStateChange:
                if self.isMinimized():
                    print("Window minimized")
            elif event.type() == QtCore.QEvent.Close:
                self.settings.save_program_config()  # Store the window size to the config file
        return super().eventFilter(watched, event)

    def show_in_statusbar(self, message: str, mode: str = None) -> None:
        """Show something in the statusbar for a little bit"""
        # Themed modes
        if mode is None:
            self.statusBar.setStyleSheet(self.statusbar_default_themes[self.settings.THEME])
        # Set special modes
        elif mode == "error":
            self.statusBar.setStyleSheet("background-color: darkred; color: white;")
        elif mode == "nothing":
            self.statusBar.setStyleSheet("")
        self.statusBar.showMessage(f"{datetime.now().strftime('%H:%M:%S')} - {message}")

    def show_popup(self, message: str) -> None:
        """Show a Pop-up with a message"""
        QtWidgets.QMessageBox.information(self, "Informacion", message)

    def ask_for_confirmation(self, message: str) -> bool:
        """Ask for confirmation and return the answer"""
        result = QtWidgets.QMessageBox.question(self, "Confirmacion", message) == QtWidgets.QMessageBox.Yes
        return result
