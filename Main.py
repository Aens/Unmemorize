# coding=utf-8
"""Code by Alejandro Gutierrez Almansa"""
from datetime import datetime
from pathlib import Path
import PySimpleGUI
import keyboard


class Notepad:
    """A virtual Notepad with all the notes stored"""

    def __init__(self):
        """Load fields from a text file"""
        self.notes = {}
        self.folderpath = Path.cwd().joinpath("notes")
        self.reload_notes()

    def reload_notes(self):
        """Clean the previous list. Crawl to get all the notes. Load them into the class"""
        self.notes.clear()
        # Load them from files
        files = list(self.folderpath.glob("*.txt"))
        for file in files:
            title = file.stem
            with open(file, encoding="UTF-8") as f:
                content = f.read()
                self.notes[title] = content


class Settings:
    """A GUI to control the notes in an easy to manage interface"""

    def __init__(self, notepad):
        """Initialize the window layour"""
        self.notepad = notepad  # Pointer to our notepad
        self.window = None

    def create_window(self):
        """Create the window"""
        # First reload the notepad
        self.notepad.reload_notes()
        # Now set the window options and setup
        layout = self.build_layout()
        self.window = PySimpleGUI.Window("LazyMode Paster", layout, finalize=True, resizable=True)
        # Initialize the window loop
        while True:
            event, values = self.window.read()
            if event == PySimpleGUI.WIN_CLOSED:
                break
            if event == 'Add Note':
                new_note_key = f'Note{len(self.notepad) + 1}'
                self.add_note(new_note_key)
                # self.show_popup(f"Field {field_number} Value: {values[event]}")  # TODO
        self.window.close()


    def build_layout(self) -> list:
        """Build the layout for the APP"""
        layout = [
            [PySimpleGUI.Button('Add Note')],
            [PySimpleGUI.Column(
                layout=[[PySimpleGUI.Text(f"{key}:"),
                         PySimpleGUI.Multiline(
                             default_text=value, key=key, autoscroll=True, write_only=True,
                             size=(None, None), expand_x=True, expand_y=True)]
                        for key, value in self.notepad.notes.items()],
                vertical_scroll_only=False, scrollable=True,
                size=(None, None), expand_x=True, expand_y=True
                )]
        ]
        return layout

    def add_note(self, key):
        # do something
        pass

    def show_popup(self, message):
        """Show a Pop-up with a message"""
        PySimpleGUI.popup(self, message)


class Keybinds:
    """Register keybinds to being able to work with this program"""

    def __init__(self, notepad, gui):
        """Register global shortcuts and pointers"""
        self.notepad = notepad
        self.gui = gui
        # keyboard.add_hotkey('alt+d', lambda: PySimpleGUI.popup_get_choice("Choose a field:", fields, title="Select Field"))  # TODO
        keyboard.add_hotkey('alt+d', self.pegar)
        keyboard.add_hotkey('alt+f', self.open_settings)

    def pegar(self):
        """Paste code"""
        print("pego codigo")

    def open_settings(self):
        """Opens the MainMenu Settings Window"""
        print("DEBUG: Abro la GUI")
        self.gui.create_window()

    @staticmethod
    def close_program():
        """Close all the needed things and close the program"""
        keyboard.unhook_all()  # Remove the hotkey to avoid conflicts after the window is closed
        exit()


##########
# LOADER #
##########
def loader():
    """Loader"""
    print(f"{datetime.now()}: Load virtual Notepad.")
    notepad = Notepad()
    print(f"{datetime.now()}: Load GUIs.")
    settings = Settings(notepad=notepad)
    print(f"{datetime.now()}: Load Keybinds.")
    keys = Keybinds(notepad=notepad, gui=settings)
    print(f"{datetime.now()}: Start endless loop and wait for commands.")
    keyboard.wait("alt+q")
    print(f"{datetime.now()}: Clean up and close this program.")
    keys.close_program()


loader()  # Initialize the program
