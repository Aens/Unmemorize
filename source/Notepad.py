# coding=utf-8
"""Code by Aens"""
import sqlite3
from datetime import datetime
from pathlib import Path


class Notepad:
    """A virtual Notepad with all the notes stored"""

    def __init__(self):
        """Load fields from a text file"""
        self.gui = None
        self.notes = {}
        self.folderpath = Path.cwd().joinpath("notes")
        self.deleted_folderpath = Path.cwd().joinpath("old_notes")
        self.reload_notes()

    def add_gui_pointer(self, gui):
        """Add a gui pointer just to call stuff from this class"""
        self.gui = gui

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

    def add_note(self, new_name):
        """Adds a new note"""
        new_note_path = self.folderpath.joinpath(f"{new_name}.txt")
        if new_note_path.exists():
            self.gui.show_popup("Error, esa nota ya existe")
            return
        else:
            try:
                with open(new_note_path, 'w', encoding="UTF-8") as file:
                    file.write("")  # Creating an empty note for now
                self.gui.show_in_statusbar(f"Nota '{new_name}' creada con exito.")
            except Exception as e:
                print(f"Error creating note '{new_name}': {e}")

    def delete_note(self, name: str) -> None:
        """It doesn't delete notes, it just moves them to a different folder"""
        source_filepath = self.folderpath.joinpath(f"{name}.txt")
        destination_filepath = self.deleted_folderpath.joinpath(f"{name}.txt")
        source_filepath.rename(destination_filepath)
        self.gui.show_in_statusbar(f"Se ha movido el fichero: {source_filepath} --> {destination_filepath}")

    def save_note(self, filename: str, value: str) -> None:
        """Saves a note with this new values"""
        new_note_path = self.folderpath.joinpath(f"{filename}.txt")
        with open(new_note_path, 'w', encoding="UTF-8") as file:
            file.write(value)  # Overwriting the content of that note
        self.gui.show_in_statusbar(f"Nota '{filename}' guardada con exito.")


class SQLNotepad:
    """A virtual Notepad with all the notes stored"""

    def __init__(self):
        """Initialize SQLite database connection and create notes table if not exists"""
        self.gui = None
        self.notes = {}
        self.db_path = Path.cwd().joinpath("notes/notes.db")
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.create_tables()  # Create tables if they don't exist
        self.reload_notes()

    def create_tables(self):
        """Create all the needed tables for the program to work with"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                title TEXT PRIMARY KEY,
                content TEXT)''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS private_notes (
                title TEXT PRIMARY KEY,
                content TEXT)''')
        self.connection.commit()

    def add_gui_pointer(self, gui):
        """Add a gui pointer just to call stuff from this class"""
        self.gui = gui

    def reload_notes(self):
        """Clean the previous list. Load notes from the database into the class"""
        self.notes.clear()
        self.cursor.execute('SELECT title, content FROM notes')
        rows = self.cursor.fetchall()
        for row in rows:
            title, content = row
            self.notes[title] = content

    def add_note(self, new_name):
        """Adds a new note to the database"""
        if new_name in self.notes:
            self.gui.show_popup("Error, esa nota ya existe")
            return
        else:
            try:
                # Insert the new note into the database
                self.cursor.execute('INSERT INTO notes (title, content) VALUES (?, ?)', (new_name, ''))
                self.connection.commit()
                self.gui.show_in_statusbar(f"Nota '{new_name}' creada con éxito.")
            except Exception as e:
                print(f"{datetime.now()} Error creating note '{new_name}': {e}")

    def delete_note(self, name: str) -> None:
        """It doesn't delete notes, it just moves them to a different folder"""
        if name in self.notes:
            try:  # TODO THIS
                # Move the note to a different folder (not implemented in this example)
                self.gui.show_in_statusbar(f"Se ha movido el fichero: {name}")
            except Exception as e:
                print(f"{datetime.now()} Error moving note '{name}': {e}")

    def save_note(self, filename: str, value: str) -> None:
        """Saves a note with these new values to the database"""
        if filename in self.notes:
            try:
                # Update the content of the existing note in the database
                self.cursor.execute('UPDATE notes SET content = ? WHERE title = ?', (value, filename))
                self.connection.commit()
                self.gui.show_in_statusbar(f"Nota '{filename}' guardada con éxito.")
            except Exception as e:
                print(f"{datetime.now()} Error saving note '{filename}': {e}")
