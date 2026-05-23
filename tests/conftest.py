import sys

import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from PySide6.QtWidgets import QApplication

TABLE_QUERIES = [
    """
    CREATE TABLE IF NOT EXISTS persons (
        person_id INTEGER PRIMARY KEY AUTOINCREMENT,
        label TEXT NOT NULL CHECK (trim(label) != ''),
        description TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS identifiers (
        identifier_id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER NOT NULL,
        hash_value TEXT NOT NULL UNIQUE,
        identifier_type TEXT NOT NULL CHECK (identifier_type IN ('QR', 'CARD')),
        FOREIGN KEY (person_id) REFERENCES persons (person_id)
        ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        label TEXT NOT NULL CHECK (label NOT IN ('')),
        description TEXT,
        start_time TEXT NOT NULL,
        duration_seconds INTEGER NOT NULL
    );
    """,
    """CREATE TABLE IF NOT EXISTS attendance (
        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER NOT NULL,
        event_id INTEGER NOT NULL,
        status INTEGER NOT NULL DEFAULT 0 CHECK (status IN (0, 1)),
        FOREIGN KEY (person_id) REFERENCES persons (person_id)
        ON DELETE CASCADE,
        FOREIGN KEY (event_id) REFERENCES events (event_id)
        ON DELETE CASCADE
    );
    """,
]


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    return app


@pytest.fixture(scope="class", autouse=True)
def database(qapp):
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(":memory:")

    if not db.open():
        pytest.fail("Unable to open database.")

    query = QSqlQuery(db)

    for table_query in TABLE_QUERIES:
        if not query.exec(table_query):
            pytest.fail(query.lastError().text())

    yield db

    db.close()

    del query
    del db


VALID_PERSON_DATA = [
    # --- Classic Names & Base Cases ---
    ("Egor Kuz", "Anonymous user for system testing purposes"),
    ("Alice Liubimova", "Backend developer from Mosvow, 19 y.o."),
    ("Mary-Jane Watson", "Actress and freelance journalist"),
    ("Alexander", ""),  # Case with None description
    # --- Extreme Lengths (Short & Long) ---
    ("J", "Single letter name, but description is standard length"),
    ("X", "X"),  # Minimum possible length for both fields
    (
        "Christopher-Maximilian-Hubertus_Vanderbilt",
        """A user with an exceptionally long first and last name to test
        how the UI or database handles text overflow, wrapping,
        and truncation algorithms without breaking layout.""",
    ),
    # --- Symbols, Numbers & Punctuation ---
    ("User_404", "Status: Active. Created via API-v2. [Internal]"),
    ("O'Connor", "Irish origin name containing an apostrophe"),
    ("id_#12345", 'Description with symbols: ~!@#$%^&*()_+{}|:"<>?'),
    ("3.14159", "Pi lover and mathematics department contact"),
    # --- Emojis & Unicode (Encoding check) ---
    ("Alex 👨‍💻", "Information security specialist 🔐"),
    ("Elon 🚀", "Going to Mars mood 🌌✨"),
    ("木村 拓哉", "Takuya Kimura - Japanese name format support check"),
    # --- Case Sensitivity & Strange Formatting ---
    ("JOHN STERN", "ALL CAPS TEXT IN BOTH FIELDS FOR TESTING"),
    ("lowercase_user", "all text here is strictly lowercase"),
    ("iNVERTED cASE", "sOME STRANGE TYPING STYLE"),
    # --- System / Technical Placeholders ---
    ("N/A", "Not Available status profile"),
    ("Undefined", ""),
    ("Unknown Person", "No data provided during the hardware scan event"),
    ("---", "---"),
    # --- Bilingual & Mixed Strings ---
    ("Peter (Петр) Perzovskiy", "Senior QA / Тестировщик автоматизатор"),
    ("Clean Code", "Refactoring enthusiast (Python, PySide6, SQL)"),
]

INVALID_PERSON_DATA = [("", ""), ("", "Test case"), ("", "Empty wizard")]
