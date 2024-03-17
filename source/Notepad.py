# coding=utf-8
"""Code by Aens"""
from datetime import datetime
import sqlite3
from pathlib import Path


class SQLNotepad:
    """A virtual Notepad with all the notes stored"""

    def __init__(self, gui):
        """Initialize SQLite database connection, create notes table if not exists and load all notes"""
        self.gui = gui
        self.notes = {}
        self.deleted_notes = {}
        # Database file
        self.db_path = Path.cwd().joinpath("notes/notes.db")
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        # Create and populate tables
        self.create_tables()

    def create_tables(self):
        """Create all the needed tables for the program to work with"""
        self.cursor.execute('CREATE TABLE IF NOT EXISTS notes '
                            '(title TEXT PRIMARY KEY, '
                            'content TEXT)''')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS notes_deleted '
                            '(title TEXT PRIMARY KEY, '
                            'content TEXT, '
                            'deleted_at TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS private_notes '
                            '(title TEXT PRIMARY KEY, '
                            'content TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS private_notes_deleted '
                            '(title TEXT PRIMARY KEY, '
                            'content TEXT, '
                            'deleted_at TEXT)')
        self.connection.commit()

    def reload_notes(self):
        """Clean the previous list. Load notes from the database into the class"""
        self.notes.clear()
        self.cursor.execute('SELECT title, content FROM notes')
        rows = self.cursor.fetchall()
        for row in rows:
            title, content = row
            self.notes[title] = content

    def reload_deleted_notes(self):
        """Clean the previous list. Load notes from the database into the class"""
        self.deleted_notes.clear()
        self.cursor.execute('SELECT title, content, deleted_at FROM notes_deleted')
        rows = self.cursor.fetchall()
        for row in rows:
            title, content, deleted_at = row
            self.deleted_notes[title] = (content, deleted_at)

    def add_note(self, new_name):
        """Adds a new note to the database"""
        if new_name in self.notes:
            self.gui.show_popup("Error, ese nombre de nota ya existe.")
            self.gui.show_in_statusbar("ERROR: Nota no creada, el nombre ya existía.", mode="error")
            return
        else:
            try:
                # Insert the new note into the database
                self.cursor.execute('INSERT INTO notes (title, content) '
                                    'VALUES (?, ?)',
                                    (new_name, ''))
                self.connection.commit()
                self.gui.show_in_statusbar(f"Nota '{new_name}' creada con éxito.")
            except Exception as e:
                self.gui.show_in_statusbar(f"ERROR: No he podido crear la nota '{new_name}': {e}", mode="error")

    def save_note(self, filename: str, value: str) -> None:
        """Saves a note with these new values to the database"""
        if filename in self.notes:
            try:
                # Update the content of the existing note in the database
                self.cursor.execute('UPDATE notes '
                                    'SET content = ? '
                                    'WHERE title = ?', (value, filename))
                self.connection.commit()
                self.gui.show_in_statusbar(f"Nota '{filename}' guardada con éxito.")
            except Exception as e:
                self.gui.show_in_statusbar(f"ERROR: No he podido guardar la nota '{filename}': {e}", mode="error")

    def delete_note(self, name: str) -> None:
        """It doesn't delete notes, it just moves them to a different table"""
        if name in self.notes:
            try:
                deleted_time = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
                # Move the note to a different table
                self.cursor.execute(f"INSERT INTO notes_deleted (title, content, deleted_at)"
                                    "SELECT title, content, ? "
                                    "FROM notes "
                                    "WHERE title = ?",
                                    (deleted_time, name))
                # Delete the note on this table
                self.cursor.execute(f"DELETE FROM notes WHERE title = ?", (name,))
                self.connection.commit()
                self.gui.show_in_statusbar(f"Se ha movido la nota: {name} a la tabla de notas borradas")
            except Exception as e:
                self.gui.show_in_statusbar(f"ERROR: No he podido mover la nota '{name}': {e}", mode="error")

    def delete_note_forever(self, name: str) -> None:
        """Permanently delete the note"""
        if name in self.deleted_notes:
            try:
                # Delete the note
                self.cursor.execute(f"DELETE FROM notes_deleted WHERE title = ?", (name,))
                self.connection.commit()
                self.gui.show_in_statusbar(f"Se ha eliminado permanentemente la nota: {name}")
            except Exception as e:
                self.gui.show_in_statusbar(f"ERROR: No he podido eliminar la nota '{name}': {e}", mode="error")

    def restore_note(self, name: str) -> None:
        """Permanently delete the note"""
        if name in self.deleted_notes:
            try:
                # Restore the note
                self.cursor.execute(f"INSERT INTO notes (title, content)"
                                    "SELECT title, content "
                                    "FROM notes_deleted "
                                    "WHERE title = ?",
                                    (name,))
                # Delete the note on this table
                self.cursor.execute(f"DELETE FROM notes_deleted WHERE title = ?", (name,))
                self.connection.commit()
                self.gui.show_in_statusbar(f"Se ha restaurado la nota: {name}.")
            except Exception as e:
                self.gui.show_in_statusbar(f"ERROR: No he podido restaurar la nota '{name}': {e}", mode="error")
