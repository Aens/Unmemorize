# coding=utf-8
"""Code by Aens"""
from datetime import datetime
import keyboard
import sys


class Keybinds:
    """Register keybinds to being able to work with this program"""

    def __init__(self, notepad, gui):
        """Register global shortcuts and pointers"""
        self.notepad = notepad
        self.gui = gui
        # keyboard.add_hotkey('alt+d', lambda: PySimpleGUI.popup_get_choice("Choose a field:", fields, title="Select Field"))  # TODO
        keyboard.add_hotkey('alt+d', self.pegar)
        keyboard.add_hotkey('alt+f', self.open_gui)

    def pegar(self):
        """Paste code"""
        print("pego codigo")

    def open_gui(self):
        """Opens the MainMenu Settings Window"""
        print("DEBUG: Abro la GUI")
        # Run the application's event loop
        self.gui.show()
        sys.exit(self.gui.app.exec())

    @staticmethod
    def close_program():
        """Close all the needed things and close the program"""
        keyboard.unhook_all()  # Remove the hotkey to avoid conflicts after the window is closed
        exit()


print(f"{datetime.now()}: Load Keybinds.")
keys = Keybinds(notepad=notepad, gui=main_window)
print(f"{datetime.now()}: Start endless loop and wait for commands.")
keys.open_gui()
keyboard.wait("alt+q")
print(f"{datetime.now()}: Clean up and close this program.")
keys.close_program()
