-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS xss_eval;

CREATE TABLE xss_eval (
    id serial PRIMARY KEY,
    payload TEXT,
    attacked_path TEXT,
    impact TEXT,
    works BOOL,
    repeated_execution BOOL
);
