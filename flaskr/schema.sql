-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS xss_eval;

CREATE TABLE xss_eval (
    id serial PRIMARY KEY,
    payload TEXT,
    attacked_path TEXT,
    structural_impact TEXT,
    console_out TEXT,
    structural_score FLOAT,
    img_score FLOAT,
    js_score FLOAT,
    response_code_score FLOAT,
    overall_score FLOAT,
    works BOOL default FALSE,
    repeated_execution BOOL default FALSE
);
