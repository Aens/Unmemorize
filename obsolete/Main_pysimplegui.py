# coding=utf-8
"""Code by Aens"""
from datetime import datetime
from pathlib import Path
import configparser
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


class GUI:
    """A GUI to control the notes in an easy to manage interface"""

    def __init__(self, notepad):
        """Initialize the window layout"""
        self.config_file = 'program_settings.ini'
        self.notepad = notepad  # Pointer to our notepad
        self.DEFAULT_WINDOW_SIZE = (800, 600)
        self.DEFAULT_WINDOW_POSITION = (200, 200)
        self.DEFAULT_WINDOW_TRANSPARENCY = 0.8
        self.window = None

    def load_window_size(self):
        """Load window size from the config file"""
        try:
            config_values = PySimpleGUI.Window().Finalize().ReadLocation(self.config_file)
            return int(config_values[0][0]), int(config_values[0][1])
        except Exception as e:
            print(e)
            return self.DEFAULT_WINDOW_SIZE

    def load_window_config(self):
        """Self-explanatory. It stores the data from a INI file"""
        config = configparser.ConfigParser()
        config.read(self.config_file)
        if config.has_section('Window'):
            size = eval(config.get('Window', 'size'))
            location = eval(config.get('Window', 'location'))
            # Set window size and location
            self.window.size = size
            self.window.set_location(location)

    def save_window_config(self):
        """Self-explanatory. It gets the data from a INI file"""
        config = configparser.ConfigParser()
        config.read(self.config_file)
        if not config.has_section('Window'):
            config.add_section('Window')
        config.set('Window', 'size', str(self.window.size))
        config.set('Window', 'location', str(self.window.current_location()))
        with open(self.config_file, 'w') as configfile:
            config.write(configfile)

    def create_window(self):
        """Create the window"""
        self.window = None
        # First reload the notepad
        self.notepad.reload_notes()
        # Load window size from the config file, set the layout and build the window
        layout = self.build_layout()
        self.window = PySimpleGUI.Window(  # We get default values before loading real ones
            title="Unmemorize", layout=layout, finalize=True, resizable=True, return_keyboard_events=True,
            element_justification='left', enable_close_attempted_event=True,
            size=self.DEFAULT_WINDOW_SIZE,
            location=self.DEFAULT_WINDOW_POSITION,
            alpha_channel=self.DEFAULT_WINDOW_TRANSPARENCY)
        # self.load_window_config()  # Load real values TODO enable later
        self.event_handler()  # Launch the event handler

    def event_handler(self):
        """Initialize the window loop and handle events"""
        while True:
            event, values = self.window.read()
            if event in (PySimpleGUI.WIN_CLOSE_ATTEMPTED_EVENT, 'Exit'):
                print("attempted")
                # The line of code to save the position before exiting
                PySimpleGUI.user_settings_set_entry('-location-', self.window.current_location())
            if event == PySimpleGUI.WIN_CLOSED:
                print(self.window.size)
                self.save_window_config()  # Store the window size to the config file
                break
            if event == 'Add Note':
                self.add_note()
                # self.show_popup(f"Field {field_number} Value: {values[event]}")  # TODO
        # Close the window after saving the configuration
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

    def add_note(self):
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
    settings = GUI(notepad=notepad)
    print(f"{datetime.now()}: Load Keybinds.")
    keys = Keybinds(notepad=notepad, gui=settings)
    print(f"{datetime.now()}: Start endless loop and wait for commands.")
    keys.open_settings()
    # keyboard.wait("alt+q")  # TODO activa para continuar
    print(f"{datetime.now()}: Clean up and close this program.")
    keys.close_program()


loader()  # Initialize the program
