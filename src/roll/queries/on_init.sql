CREATE TABLE IF NOT EXISTS persons (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL CHECK (trim(label) != ''),
    description TEXT
);

CREATE TABLE IF NOT EXISTS identifiers (
    identifier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    hash_value TEXT NOT NULL UNIQUE,
    identifier_type TEXT NOT NULL CHECK (identifier_type IN ('QR', 'CARD')),
    FOREIGN KEY (person_id) REFERENCES persons (person_id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL CHECK (label NOT IN ('')),
    description TEXT,
    start_time TEXT NOT NULL, -- Format: 'YYYY-MM-DDTHH:MM:SS'
    duration_seconds INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    status INTEGER NOT NULL DEFAULT 0 CHECK (status IN (0, 1)), -- 0 absent, 1 present
    FOREIGN KEY (person_id) REFERENCES persons (person_id)
    ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events (event_id)
    ON DELETE CASCADE
);
