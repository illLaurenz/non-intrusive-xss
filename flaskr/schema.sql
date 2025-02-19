-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS xss;
DROP TABLE IF EXISTS post;

CREATE TABLE xss (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payload TEXT,
    attacked_path TEXT,
    impact TEXT,
    works BOOL,
    repeated_execution BOOL
);
