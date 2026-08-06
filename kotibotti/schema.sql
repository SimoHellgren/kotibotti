PRAGMA user_version = 1;

CREATE TABLE IF NOT EXISTS item (
    id INTEGER PRIMARY KEY,
    kind TEXT, -- e.g. 'freezer'
    data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);