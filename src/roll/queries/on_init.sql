-- Таблица persons
CREATE TABLE IF NOT EXISTS persons (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL,
    description TEXT
);

-- Таблица events
CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL,
    description TEXT,
    start_time TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL
);

-- Таблица identifiers
CREATE TABLE IF NOT EXISTS identifiers (
    identifier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    hash_value TEXT NOT NULL UNIQUE,
    identifier_type TEXT NOT NULL,
    FOREIGN KEY (person_id) REFERENCES persons(person_id) ON DELETE CASCADE
);

-- Таблица attendance
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    status INTEGER NOT NULL DEFAULT 1,
    check_in_time TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES persons(person_id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_identifiers_hash ON identifiers(hash_value);
CREATE INDEX IF NOT EXISTS idx_attendance_event ON attendance(event_id);
CREATE INDEX IF NOT EXISTS idx_attendance_person ON attendance(person_id);