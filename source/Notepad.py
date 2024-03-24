# coding=utf-8
"""Code by Aens"""
from datetime import datetime
import sqlite3
from pathlib import Path
import shutil


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

    def reload_notes(self):
        """Clean the previous list. Load notes from the database into the class"""
        self.notes.clear()
        self.cursor.execute('SELECT id, title, content FROM notes')
        rows = self.cursor.fetchall()
        for row in rows:
            _id, title, content = row
            self.notes[_id] = (title, content)

    def reload_deleted_notes(self):
        """Clean the previous list. Load notes from the database into the class"""
        self.deleted_notes.clear()
        self.cursor.execute('SELECT id, title, content, deleted_at FROM notes_deleted')
        rows = self.cursor.fetchall()
        for row in rows:
            _id, title, content, deleted_at = row
            self.deleted_notes[_id] = (title, content, deleted_at)

    def add_note(self, new_name: str):
        """Adds a new note to the database"""
        try:
            # Insert the new note into the database
            self.cursor.execute('INSERT INTO notes (id, title, content) '
                                'VALUES (NULL, ?, NULL)',
                                (new_name,))
            self.connection.commit()
            self.gui.show_in_statusbar(f"Nota '{new_name}' creada con éxito.")
        except Exception as e:
            self.gui.show_in_statusbar(f"ERROR: No he podido crear la nota '{new_name}': {e}", mode="error")

    def save_note(self, _id: int, filename: str, value: str) -> None:
        """Saves a note with these new values to the database"""
        if _id in self.notes:
            try:
                # Update the content of the existing note in the database
                self.cursor.execute('UPDATE notes '
                                    'SET content = ? '
                                    'WHERE id = ?', (value, _id))
                self.connection.commit()
                self.gui.show_in_statusbar(f"Nota '{filename}' guardada con éxito.")
            except Exception as e:
                self.gui.show_in_statusbar(f"ERROR: No he podido guardar la nota '{filename}': {e}", mode="error")

    def delete_note(self, _id: int, name: str) -> None:
        """It doesn't delete notes, it just moves them to a different table"""
        if _id in self.notes:
            try:
                deleted_time = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
                # Move the note to a different table
                self.cursor.execute(f"INSERT INTO notes_deleted (title, content, deleted_at)"
                                    "SELECT title, content, ? "
                                    "FROM notes "
                                    "WHERE id = ?",
                                    (deleted_time, _id))
                # Delete the note on this table
                self.cursor.execute(f"DELETE FROM notes WHERE id = ?", (_id,))
                self.connection.commit()
                self.gui.show_in_statusbar(f"Se ha movido la nota: {name} a la tabla de notas borradas")
            except Exception as e:
                self.gui.show_in_statusbar(f"ERROR: No he podido mover la nota '{name}': {e}", mode="error")

    def delete_note_forever(self, _id: int, name: str) -> None:
        """Permanently delete the note"""
        if _id in self.deleted_notes:
            try:
                # Delete the note
                self.cursor.execute(f"DELETE FROM notes_deleted WHERE id = ?", (_id,))
                self.connection.commit()
                self.gui.show_in_statusbar(f"Se ha eliminado permanentemente la nota: {name}")
            except Exception as e:
                self.gui.show_in_statusbar(f"ERROR: No he podido eliminar la nota '{name}': {e}", mode="error")

    def restore_note(self, _id: int, name: str) -> None:
        """Permanently delete the note"""
        if _id in self.deleted_notes:
            try:
                # Restore the note
                self.cursor.execute(f"INSERT INTO notes (title, content)"
                                    "SELECT title, content "
                                    "FROM notes_deleted "
                                    "WHERE id = ?",
                                    (_id,))
                # Delete the note on this table
                self.cursor.execute(f"DELETE FROM notes_deleted WHERE id = ?", (_id,))
                self.connection.commit()
                self.gui.show_in_statusbar(f"Se ha restaurado la nota: {name}.")
            except Exception as e:
                self.gui.show_in_statusbar(f"ERROR: No he podido restaurar la nota '{name}': {e}", mode="error")


class PrepareDatabase:
    """Class that makes sure your database is correctc"""

    def __init__(self):
        """Initialize SQLite database connection and check if we need to fix something"""
        self.connection = None
        # IF database file doesn't exists
        self.db_path = Path.cwd().joinpath("notes/notes.db")
        db_exists = self.db_path.exists()  # Store temporary
        self.connection = sqlite3.connect(self.db_path)  # Because this line creates the file automatically
        self.cursor = self.connection.cursor()
        if not db_exists:
            self.create_database_tables()
        # IF database is missing some columns
        self.check_if_fixes_are_needed()

    def create_database_tables(self) -> None:
        """Create all the needed tables for the program to work with"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes 
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, 
            content TEXT,
            test TEXT,
            otro TEXT,
            algo TEXT)
            """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes_deleted 
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, 
            content TEXT, 
            deleted_at TEXT)
            """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS private_notes 
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, 
            content TEXT)
            """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS private_notes_deleted 
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, 
            content TEXT, 
            deleted_at TEXT)
            """)
        self.connection.commit()

    def check_if_fixes_are_needed(self) -> None:
        """Check if we have all the needed databases with the correct columns"""
        tables = {
            "notes":                 ['id', 'title', 'content', "test", "otro", "algo"],
            "notes_deleted":         ['id', 'title', 'content', 'deleted_at'],
            "private_notes":         ['id', 'title', 'content'],
            "private_notes_deleted": ['id', 'title', 'content', 'deleted_at']
        }
        tables_to_fix = []
        # 1 - Check if the table doesn't have all the required columns
        for table, columns in tables.items():
            if not self.check_table_columns(table, columns):
                tables_to_fix.append(table)  # Missing some columns
        # 2 - For those identified to have missing values, fix them
        if tables_to_fix:
            # 2.1 - First, create a backup of the entire thing
            self.create_database_backup()
            # 2.2 - Second, fix the columns in the current database
            self.fix_tables(tables_to_fix)

    def fix_tables(self, tables_to_fix: list) -> None:
        """Make sure to create the missing columns in the tables"""
        # 1 - Copy data to a temp table and delete original table
        for table in tables_to_fix:
            # In order to ignore the auto-increment column, we need to get column names and then remove it
            columns = self.cursor.execute(f"PRAGMA table_info('{table}')")
            column_names = ", ".join([col[1] for col in columns if col[1] != 'id'])  # We ignore ID column
            # Now copy to the temporary column all data except ID column
            self.cursor.execute(f"CREATE TABLE temp_{table} AS SELECT {column_names} FROM {table};")
            self.cursor.execute(f"DROP TABLE {table};")
        # 2 - Recreate original tables with the good scheme this time
        self. create_database_tables()
        # 3 - Copy data back to the tables and delete temp tables
        for table in tables_to_fix:
            # Get the number of columns of both new table and temporal table
            columns_new = self.cursor.execute(f"PRAGMA table_info('{table}')")
            column_names_new = [col[1] for col in columns_new if col[1] != 'id']
            columns_temp = self.cursor.execute(f"PRAGMA table_info('temp_{table}')")
            column_names_temp = [col[1] for col in columns_temp]
            # Build a list of NULLS with the amount of new added columns
            new_empty_fields = (len(column_names_new) - len(column_names_temp))
            new_empty_fields = ', '.join(["NULL"] * new_empty_fields) if new_empty_fields > 1 else "NULL"
            try:
                self.cursor.execute(f"INSERT INTO {table} SELECT NULL, *, {new_empty_fields} FROM temp_{table};")
            except sqlite3.OperationalError:
                self.cursor.execute(f"INSERT INTO {table} SELECT NULL, * FROM temp_{table};")
            self.cursor.execute(f"DROP TABLE temp_{table};")
        # 4 - Save all changes
        self.connection.commit()

    def create_database_backup(self) -> None:
        """Create a database backup just in case"""
        time_now = datetime.strftime(datetime.now(), "%y-%m-%d %H_%M_%S")
        backup_db_path = Path.cwd().joinpath(f"notes/notes_backup_{time_now}.db")
        shutil.copy(self.db_path, backup_db_path)
        print("Database structure needs update, so I've created a backup in the Notes folder")

    def check_table_columns(self, table_name: str, required_columns: list) -> bool:
        """Check if all columns exists in a table"""
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = [row[1] for row in self.cursor.fetchall()]
        for column in required_columns:
            if column not in existing_columns:
                return False
        return True
