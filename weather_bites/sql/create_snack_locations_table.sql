/* creating db table for snack_locations */
CREATE TABLE snack_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    rating FLOAT DEFAULT 0.0
    favorite BOOLEAN DEFAULT FALSE
    review TEXT DEFAULT NULL
);

