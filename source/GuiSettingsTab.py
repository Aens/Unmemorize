# coding=utf-8
"""Code by Aens"""
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QSize, QPoint


class SettingsTab:
    """A Tab to deal with Settings, it is expected to hold the settings in cache as properties of this class"""

    def __init__(self, gui):
        """Initialize all the options needed for this tab to work"""
        self.gui = gui  # <-- Pointer to the main GUI
        self.this_tab = self.gui.settings_tab  # <-- Pointer to what holds this tab
        self.notepad = self.gui.notepad  # <-- Pointer for lazyness, to not call the gui all the time
        self.notes_scroll_layout = None  # <-- Pointer so we can reload this tab later
        self.settings_file = QtCore.QSettings('program_settings.ini', QtCore.QSettings.IniFormat)
        # Settings
        self.AUTOSAVE = False
        self.THEME = 0
        self.NOTES_ROWS = 0
        # Initialize
        self.load_program_config()  # Override default settings with the ones from file
        self.create_settings_tab()  # Create the new tab

    ###############
    # LOAD/UNLOAD #
    ###############

    def load_program_config(self) -> None:
        """Self-explanatory. It stores the data from a INI file"""
        self.gui.setWindowOpacity(1)
        # Try to find the settings or just load the default values
        self.gui.resize(self.settings_file.value("Window/size", QSize(800, 600)))
        self.gui.move(self.settings_file.value("Window/location", QPoint(200, 200)))
        self.AUTOSAVE = self.settings_file.value("Settings/autosave_notes", "false", bool)
        self.THEME = self.settings_file.value("Settings/theme", 0, int)
        self.NOTES_ROWS = self.settings_file.value("Settings/notes_rows", 4, int)
        self.change_stylesheet(style=self.THEME)

    def save_program_config(self) -> None:
        """Self-explanatory. It gets the data from a INI file"""
        self.settings_file.setValue("Window/size", self.gui.size())
        self.settings_file.setValue("Window/location", self.gui.pos())
        self.settings_file.setValue("Settings/autosave_notes", self.AUTOSAVE)
        self.settings_file.setValue("Settings/theme", self.THEME)
        self.settings_file.setValue("Settings/notes_rows", self.NOTES_ROWS)

    ##########
    # LAYOUT #
    ##########

    def create_settings_tab(self) -> None:
        """Create the settings tab and set its layout"""
        # 1 - Stylesheets
        stylesheet_label = QtWidgets.QLabel("Estilo del programa:")
        stylesheet_combobox = QtWidgets.QComboBox()
        stylesheet_combobox.addItem("Gris")
        stylesheet_combobox.addItem("Oscuro")
        stylesheet_combobox.addItem("Azul")
        stylesheet_combobox.addItem("Verde")
        # 2 - AutoSave
        auto_save_checkbox = QtWidgets.QCheckBox("Guardar Notas Automáticamente")
        auto_save_checkbox.setChecked(self.AUTOSAVE)  # Set the initial state
        # 3 - Layout options
        notes_layout_rows_label = QtWidgets.QLabel("Filas de Notas: ")
        notes_layout_rows = QtWidgets.QSpinBox()
        notes_layout_rows.setRange(1, 20)
        notes_layout_rows.setValue(4)

        # Set up a grid layout for the label and combobox
        settings_layout = QtWidgets.QGridLayout(self.this_tab)
        settings_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)  # Align to top-left
        # Set up the items
        settings_layout.addWidget(stylesheet_label, 0, 0)  # Label in the first row, first column
        settings_layout.addWidget(stylesheet_combobox, 0, 1)  # Combobox in the first row, second column
        settings_layout.addWidget(auto_save_checkbox, 1, 0, 1, 2)  # Combobox in the first row, second column
        settings_layout.addWidget(notes_layout_rows_label, 2, 0)  # Combobox in the first row, second column
        settings_layout.addWidget(notes_layout_rows, 2, 1)  # Combobox in the first row, second column
        # Connections/Events
        stylesheet_combobox.currentIndexChanged.connect(self.change_stylesheet)
        auto_save_checkbox.stateChanged.connect(self.handle_auto_save_checkbox)
        notes_layout_rows.valueChanged.connect(self.change_amount_of_rows)

    ############
    # SETTINGS #
    ############

    def handle_auto_save_checkbox(self, state: int) -> None:
        """Disable or enable the auto-saving
           :param state: values can be 0 or 2"""
        if state:
            self.AUTOSAVE = True
        else:
            self.AUTOSAVE = False

    def change_stylesheet(self, style: int) -> None:
        """Change the application stylesheet"""
        style = str(style)
        mapped_options = {
            "0": "resources/theme_gray.QSS",
            "1": "resources/theme_dark.QSS",
            "2": "resources/theme_light.QSS",
            "3": "resources/theme_green.QSS"}
        with open(mapped_options[style], encoding="UTF-8") as file:
            stylesheet = file.read()
        self.THEME = style
        self.gui.app.setStyleSheet(stylesheet)

    def change_amount_of_rows(self, value: int) -> None:
        """Reload the notes with a fixed amount
           :param value: values can be from 1 to 20"""
        self.NOTES_ROWS = value
        self.gui.notes.reload_notes_layout()
        self.gui.show_in_statusbar(f"Notas recargadas. Cantidad de filas: {value}")
