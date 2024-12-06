/* creating db table for snack_locations */
CREATE TABLE ReviewsTable (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    rating INTEGER DEFAULT 0 CHECK (rating >= 1 AND rating <= 5),
    favorite BOOLEAN DEFAULT FALSE,
    review TEXT DEFAULT NULL
);

