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
        # Pointers to some specific elements to call them from outside the constructor
        self.stylesheet_combobox = QtWidgets.QComboBox()
        self.auto_save_checkbox = QtWidgets.QCheckBox("Guardar Notas Automáticamente")
        self.notes_layout_combobox = QtWidgets.QComboBox()
        self.notes_layout_columns = QtWidgets.QSpinBox()
        self.notes_layout_rows = QtWidgets.QSpinBox()
        # Settings
        self.AUTOSAVE = False
        self.THEME = 0
        self.NOTES_LAYOUT = 0
        self.NOTES_ROWS = 0
        self.NOTES_COLUMNS = 0
        self.load_program_config()  # Override default settings with the ones from file
        # Initialize
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
        self.NOTES_LAYOUT = self.settings_file.value("Settings/notes_layout", 0, int)
        self.NOTES_ROWS = self.settings_file.value("Settings/notes_rows", 4, int)
        self.NOTES_COLUMNS = self.settings_file.value("Settings/notes_columns", 5, int)
        self.change_stylesheet(style=self.THEME)

    def save_program_config(self) -> None:
        """Self-explanatory. It gets the data from a INI file"""
        self.settings_file.setValue("Window/size", self.gui.size())
        self.settings_file.setValue("Window/location", self.gui.pos())
        self.settings_file.setValue("Settings/autosave_notes", self.AUTOSAVE)
        self.settings_file.setValue("Settings/theme", self.THEME)
        self.settings_file.setValue("Settings/notes_layout", self.NOTES_LAYOUT)
        self.settings_file.setValue("Settings/notes_rows", self.NOTES_ROWS)
        self.settings_file.setValue("Settings/notes_columns", self.NOTES_COLUMNS)

    ##########
    # LAYOUT #
    ##########

    def create_settings_tab(self) -> None:
        """Create the settings tab and set its layouts"""
        # 1 - Stylesheets
        group_box_stylesheet = QtWidgets.QGroupBox('Paleta de colorinchis')
        layout_stylesheet = QtWidgets.QGridLayout()
        # controls
        stylesheet_label = QtWidgets.QLabel("Estilo del programa:")
        self.stylesheet_combobox.addItem("Gris")
        self.stylesheet_combobox.addItem("Oscuro")
        self.stylesheet_combobox.addItem("Azul")
        self.stylesheet_combobox.addItem("Verde")
        self.stylesheet_combobox.setCurrentIndex(self.THEME)  # Set the initial state from memory
        self.stylesheet_combobox.setToolTip('Cambia el estilo de todo el programa. Puede ser necesario un reinicio.')
        # add to layout
        layout_stylesheet.addWidget(stylesheet_label, 0, 0)
        layout_stylesheet.addWidget(self.stylesheet_combobox, 0, 1)
        group_box_stylesheet.setLayout(layout_stylesheet)

        # 2 - AutoSave
        group_box_checkboxes = QtWidgets.QGroupBox('Opciones generales')
        layout_checkboxes = QtWidgets.QGridLayout()
        # controls
        self.auto_save_checkbox.setChecked(self.AUTOSAVE)  # Set the initial state from memory
        self.auto_save_checkbox.setToolTip('Auto-guarda la nota al sacar el puntero del área de la nota')
        # add to layout
        layout_checkboxes.addWidget(self.auto_save_checkbox, 1, 0, 1, 2)
        group_box_checkboxes.setLayout(layout_checkboxes)

        # 3 - Notes Layout options
        group_box_notes_layout = QtWidgets.QGroupBox('Interfaz de las notas')
        layout_notes_layout = QtWidgets.QGridLayout()
        # controls
        layout_label = QtWidgets.QLabel("Scroll infinito para las notas: ")
        self.notes_layout_combobox.addItem("Vertical")
        self.notes_layout_combobox.addItem("Horizontal")
        self.notes_layout_combobox.setCurrentIndex(self.NOTES_LAYOUT)  # Set the initial state from memory
        self.notes_layout_combobox.setToolTip('Reconfigura el panel de notas para scroll Vertical u Horizontal.')
        # rows
        notes_layout_rows_label = QtWidgets.QLabel("Cantidad de Filas: ")
        self.notes_layout_rows.setRange(1, 20)
        self.notes_layout_rows.setValue(4)
        self.notes_layout_rows.setToolTip('Solo modificable en modo Horizontal')
        self.notes_layout_rows.setDisabled(True if self.NOTES_LAYOUT == 0 else False)
        # cols
        notes_layout_columns_label = QtWidgets.QLabel("Cantidad de Columnas: ")
        self.notes_layout_columns.setRange(1, 20)
        self.notes_layout_columns.setValue(4)
        self.notes_layout_columns.setToolTip('Solo modificable en modo Vertical')
        self.notes_layout_columns.setDisabled(True if self.NOTES_LAYOUT == 1 else False)
        # add to layout
        layout_notes_layout.addWidget(layout_label, 0, 0)
        layout_notes_layout.addWidget(self.notes_layout_combobox, 0, 1)
        layout_notes_layout.addWidget(notes_layout_rows_label, 1, 0)
        layout_notes_layout.addWidget(self.notes_layout_rows, 1, 1)
        layout_notes_layout.addWidget(notes_layout_columns_label, 2, 0)
        layout_notes_layout.addWidget(self.notes_layout_columns, 2, 1)
        group_box_notes_layout.setLayout(layout_notes_layout)

        # Set up a grid layout for the label and combobox
        settings_layout = QtWidgets.QGridLayout(self.this_tab)
        settings_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)  # Align to top-left
        # Set up the items
        settings_layout.addWidget(group_box_stylesheet, 0, 0)
        settings_layout.addWidget(group_box_checkboxes, 1, 0)
        settings_layout.addWidget(group_box_notes_layout, 2, 0)

        # Connections/Events
        self.stylesheet_combobox.currentIndexChanged.connect(self.change_stylesheet)
        self.auto_save_checkbox.stateChanged.connect(self.handle_auto_save_checkbox)
        self.notes_layout_combobox.currentIndexChanged.connect(self.change_notes_layout)
        self.notes_layout_rows.valueChanged.connect(self.change_amount_of_rows)
        self.notes_layout_columns.valueChanged.connect(self.change_amount_of_columns)

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
        mapped_options = {
            "0": "resources/theme_gray.QSS",
            "1": "resources/theme_dark.QSS",
            "2": "resources/theme_light.QSS",
            "3": "resources/theme_green.QSS"}
        with open(mapped_options[str(style)], encoding="UTF-8") as file:
            stylesheet = file.read()
        self.THEME = style
        self.gui.app.setStyleSheet(stylesheet)

    def change_notes_layout(self, style: int) -> None:
        """Change the layout of the notes: horizontal or vertical"""
        if style == 0:  # Vertical
            self.notes_layout_rows.setDisabled(True)
            self.notes_layout_columns.setDisabled(False)
        elif style == 1:  # Horizontal
            self.notes_layout_rows.setDisabled(False)
            self.notes_layout_columns.setDisabled(True)
        self.NOTES_LAYOUT = style
        self.gui.notes.reload_notes_layout()

    def change_amount_of_rows(self, value: int) -> None:
        """Reload the notes with a fixed amount of rows
           :param value: values can be from 1 to 20"""
        self.NOTES_ROWS = value
        self.gui.notes.reload_notes_layout()
        self.gui.show_in_statusbar(f"Notas recargadas. Cantidad de filas: {value}")

    def change_amount_of_columns(self, value: int) -> None:
        """Reload the notes with a fixed amount of columns
           :param value: values can be from 1 to 20"""
        self.NOTES_COLUMNS = value
        self.gui.notes.reload_notes_layout()
        self.gui.show_in_statusbar(f"Notas recargadas. Cantidad de columnas: {value}")