from dataclasses import dataclass
from pathlib import Path
from typing import List
import fugashi
import logging
import sqlite3

DATABASE_ROOT = "data/real_db.db"


def _initialize_database(db_path: str) -> None:
    db_file = Path(db_path)
    if not db_file.parent.exists() and db_file.parent != Path('.'):
        db_file.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")

        create_sourcefiles_table = """
        CREATE TABLE IF NOT EXISTS SourceFiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL
        );
        """

        create_kanjiappearances_table = """
        CREATE TABLE IF NOT EXISTS KanjiAppearances (
            kanji TEXT NOT NULL,
            sourcefile_id INTEGER NOT NULL,
            line_number INTEGER NOT NULL,
            FOREIGN KEY (sourcefile_id) REFERENCES SourceFiles(id),
            PRIMARY KEY (kanji, sourcefile_id, line_number)
        );
        """

        create_baseformappearances_table = """
        CREATE TABLE IF NOT EXISTS BaseFormAppearances (
            baseform TEXT NOT NULL,
            sourcefile_id INTEGER NOT NULL,
            line_number INTEGER NOT NULL,
            FOREIGN KEY (sourcefile_id) REFERENCES SourceFiles(id),
            PRIMARY KEY (baseform, sourcefile_id, line_number)
        );
        """

        create_idx_kanji_appearances = """
        CREATE INDEX IF NOT EXISTS idx_kanji_appearances 
        ON KanjiAppearances (kanji, sourcefile_id, line_number);
        """

        create_idx_baseform_appearances = """
        CREATE INDEX IF NOT EXISTS idx_baseform_appearances 
        ON BaseFormAppearances (baseform, sourcefile_id, line_number);
        """

        conn.executescript(f"""
        {create_sourcefiles_table}
        {create_kanjiappearances_table}
        {create_baseformappearances_table}
        """)

        conn.executescript(f"""
        {create_idx_kanji_appearances}
        {create_idx_baseform_appearances}
        """)


def initialize_database(db_path: str) -> None:
    try:
        _initialize_database(db_path)
        logging.info(f"Database initialized successfully at '{db_path}'.")
    except sqlite3.Error as e:
        logging.error(f"An error occurred while initializing the database: {e}")


def get_db_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_source_file_id(conn: sqlite3.Connection, filename: str) -> int:
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM SourceFiles WHERE filename = ?
        """, (filename,))
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            return -1
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return -1


def add_source_file(conn: sqlite3.Connection, filename: str) -> int:
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO SourceFiles (filename)
            VALUES (?)
        """, (filename,))
        conn.commit()
        cursor.execute("""
            SELECT id FROM SourceFiles WHERE filename = ?
        """, (filename,))
        return cursor.fetchone()[0]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return -1


def add_kanji_appearances(
    conn: sqlite3.Connection,
    kanji_list: List[str],
    sourcefile_id: int,
    line_number: int,
    max_appearances: int = 50
) -> None:
    try:
        cursor = conn.cursor()

        for kanji in kanji_list:
            cursor.execute("""
                INSERT OR IGNORE INTO KanjiAppearances (kanji, sourcefile_id, line_number)
                SELECT ?, ?, ?
                WHERE (
                    SELECT COUNT(*)
                    FROM KanjiAppearances
                    WHERE kanji = ?
                ) < ?
            """, (kanji, sourcefile_id, line_number, kanji, max_appearances))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")


def add_baseform_appearances(
    conn: sqlite3.Connection,
    baseform_list: List[str],
    sourcefile_id: int,
    line_number: int,
    max_appearances: int = 20
) -> None:
    try:
        cursor = conn.cursor()

        for baseform in baseform_list:
            cursor.execute("""
                INSERT OR IGNORE INTO BaseFormAppearances (baseform, sourcefile_id, line_number)
                SELECT ?, ?, ?
                WHERE (
                    SELECT COUNT(*)
                    FROM BaseFormAppearances
                    WHERE baseform = ?
                ) < ?
            """, (baseform, sourcefile_id, line_number, baseform, max_appearances))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")


def get_baseform(tagger: fugashi.Tagger, word: str) -> str:
    for word_obj in tagger(word):
        base_form = word_obj.feature.lemma or word_obj.surface
        if base_form:
            return base_form
    return word


@dataclass
class SourceLocation:
    filename: str
    line_number: int


def get_source_locations_for_baseform(conn: sqlite3.Connection, baseform: str) -> List[SourceLocation]:
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT sf.filename, bfa.line_number
            FROM BaseFormAppearances bfa
            JOIN SourceFiles sf ON bfa.sourcefile_id = sf.id
            WHERE bfa.baseform = ?
            ORDER BY sf.filename, bfa.line_number
        """, (baseform,))

        return [
            SourceLocation(
                filename=row['filename'],
                line_number=row['line_number']
            ) for row in cursor.fetchall()
        ]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def get_source_locations_for_kanji(conn: sqlite3.Connection, kanji: str) -> List[SourceLocation]:
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT sf.filename, ka.line_number
            FROM KanjiAppearances ka
            JOIN SourceFiles sf ON ka.sourcefile_id = sf.id
            WHERE ka.kanji = ?
            ORDER BY sf.filename, ka.line_number
        """, (kanji,))

        return [
            SourceLocation(
                filename=row['filename'],
                line_number=row['line_number']
            ) for row in cursor.fetchall()
        ]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
