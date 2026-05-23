import sys
from datetime import UTC, datetime, timedelta

import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from PySide6.QtWidgets import QApplication

# TODO (asnden): make invalid data for event and event DTO
# TODO (asnden): make (in)valid data for person DTO

# TODO (asnden): Move this to another file
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


VALID_EVENT_DATA = [
    # --- Classic Names & Base Cases ---
    (
        "Math Lecture #1",
        datetime(2026, 9, 1, 9, 0, tzinfo=UTC),
        timedelta(hours=1, minutes=30),
        "Standard university lecture. Attendance via paper roster.",
    ),
    (
        "Daily Sync | Team Alpha",
        datetime(2026, 5, 25, 10, 0, tzinfo=UTC),
        timedelta(minutes=15),
        "Quick corporate check-in. Zoom participant log active.",
    ),
    (
        "UI/UX Design Masterclass",
        datetime(2026, 5, 28, 14, 0, tzinfo=UTC),
        timedelta(hours=2, minutes=45),
        "Guest speaker session. Digital certificates based on attendance.",
    ),
    (
        "Onboarding Session",
        datetime(2026, 6, 1, 11, 0, tzinfo=UTC),
        timedelta(hours=1),
        "",
    ),  # Case with empty description
    # --- Extreme Lengths (Short & Long) ---
    (
        "Q",
        datetime(2026, 5, 25, 12, 0, tzinfo=UTC),
        timedelta(minutes=5),
        "Single letter event name, but description is standard length.",
    ),
    (
        "X",
        datetime(2026, 5, 25, 0, 0, tzinfo=UTC),
        timedelta(seconds=1),
        "X",
    ),  # Minimum possible length for text fields and duration
    (
        "International-Symposium-On-Advanced-Quantum-Computing-And-Neural-Networks-2026",
        datetime(2026, 11, 12, 9, 30, tzinfo=UTC),
        timedelta(hours=8),
        """A very long event name to test how UI table cells, calendars, and text
        truncation algorithms handle layout overflow
        without breaking the dashboard interface.""",
    ),
    # --- Symbols, Numbers & Punctuation ---
    (
        "Event_ID_404: Emergency Sync",
        datetime(2026, 5, 26, 16, 45, tzinfo=UTC),
        timedelta(minutes=20),
        "Status: Urgent. Roll call via Slack bot reactions. [Internal]",
    ),
    (
        "Rock'n'Roll Dance Class",
        datetime(2026, 5, 29, 19, 0, tzinfo=UTC),
        timedelta(hours=1, minutes=30),
        "Studio event containing an apostrophe in title. Check-in at the door.",
    ),
    (
        "Session_#12345",
        datetime(2026, 10, 5, 13, 0, tzinfo=UTC),
        timedelta(hours=2),
        'Description with symbols for validation: ~!@#$%^&*()_+{}|:"<>?',
    ),
    (
        "3.14159: Pi Day Meetup",
        datetime(2026, 3, 14, 15, 9, tzinfo=UTC),
        timedelta(hours=3, minutes=14),
        "Mathematics department annual gathering. Attendance sheet signed in ink.",
    ),
    # --- Emojis & Unicode (Encoding check) ---
    (
        "Python Hackathon 💻🔥",
        datetime(2026, 10, 10, 10, 0, tzinfo=UTC),
        timedelta(hours=12),
        "Code marathon 🚀 Check-in via Discord bot commands 🔐",
    ),
    (
        "Space Tech Keynote 🌌✨",
        datetime(2026, 12, 1, 18, 0, tzinfo=UTC),
        timedelta(hours=1, minutes=15),
        "Mars mission status update. QR-code scan at the main gates.",
    ),
    (
        "日本語能力試験対策講座",
        datetime(2026, 9, 5, 14, 0, tzinfo=UTC),
        timedelta(hours=2),
        "JLPT Exam Preparation Course - Japanese character support validation check.",
    ),
    # --- Case Sensitivity & Strange Formatting ---
    (
        "MANDATORY ALL-HANDS MEETING",
        datetime(2026, 6, 15, 15, 0, tzinfo=UTC),
        timedelta(hours=2),
        "ALL CAPS TEXT IN BOTH FIELDS FOR ATTENDANCE COMPLIANCE TESTING",
    ),
    (
        "lowercase_seminar_v3",
        datetime(2026, 5, 27, 10, 30, tzinfo=UTC),
        timedelta(minutes=45),
        "all text elements here are strictly lowercase for string manipulation checks",
    ),
    (
        "iNVERTED cASE cLASS",
        datetime(2026, 5, 27, 16, 0, tzinfo=UTC),
        timedelta(hours=1),
        "sOME STRANGE TYPING STYLE FOR PARSING VALIDATION",
    ),
    # --- System / Technical Placeholders ---
    (
        "N/A",
        datetime(2026, 5, 25, 8, 0, tzinfo=UTC),
        timedelta(minutes=30),
        "Not Available status or unassigned calendar block validation.",
    ),
    (
        "Unknown Event",
        datetime(2026, 5, 25, 23, 59, tzinfo=UTC),
        timedelta(minutes=1),
        "No data provided during the hardware barcode scanner automated event capture.",
    ),
    (
        "---",
        datetime(2026, 5, 25, 12, 0, tzinfo=UTC),
        timedelta(hours=24),
        "---",
    ),  # 24-hour duration boundary test with placeholder strings
    # --- Bilingual & Mixed Strings ---
    (
        "QA Sync",
        datetime(2026, 5, 26, 11, 30, tzinfo=UTC),
        timedelta(hours=1, minutes=15),
        "Automation testing alignment / Сверка присутствия инженеров",
    ),
    (
        "Clean Code Workshop [PySide6]",
        datetime(2026, 6, 20, 13, 0, tzinfo=UTC),
        timedelta(hours=4, minutes=30),
        "Refactoring enthusiast meetup (Python, GUI, SQL)",
    ),
]

INVALID_EVENT_DATA = [
    # --- Empty label ---
    (
        "",
        datetime(2026, 6, 20, 13, 0, tzinfo=UTC),
        timedelta(hours=4, minutes=30),
        "No label",
    ),
    (
        "",
        datetime(2026, 6, 20, 13, 0, tzinfo=UTC),
        timedelta(hours=4, minutes=30),
        "",
    ),
    # --- Zero duration ---
    (
        "Clean Code Workshop [PySide6]",
        datetime(2026, 6, 20, 13, 0, tzinfo=UTC),
        timedelta(seconds=0),
        "Refactoring enthusiast meetup (Python, GUI, SQL)",
    ),
    (
        "QA Sync",
        datetime(2026, 5, 26, 11, 30, tzinfo=UTC),
        timedelta(seconds=0),
        "Automation testing alignment / Сверка присутствия инженеров",
    ),
]

VALID_UPDATE_EVENT_DTO_DATA = [
    # --- Base Case: Update all fields ---
    (
        "Urgent Retrospective",
        datetime(2026, 5, 25, 16, 0, tzinfo=UTC),
        timedelta(hours=1),
        "Emergency sync up regarding latest infrastructure failure.",
    ),
    # --- Partial Updates ---
    ("Renamed Event Only", None, None, None),
    (None, datetime(2026, 6, 1, 9, 0, tzinfo=UTC), None, None),
    (None, None, timedelta(minutes=45), None),
    (None, None, None, "Updated description text. Attendance via new dashboard link."),
    # --- Mixed Updates ---
    ("Python Core Workshop", None, timedelta(hours=3), None),
    (None, datetime(2026, 5, 26, 14, 0, tzinfo=UTC), timedelta(minutes=15), None),
    # --- Edge Cases & Boundaries ---
    (None, None, None, ""),
    (
        None,
        datetime(2026, 12, 31, 23, 59, tzinfo=UTC),
        timedelta(seconds=1),
        "System health check at the very last second of the year.",
    ),
]
