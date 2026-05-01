CREATE_REVIEWS_TABLE = """
CREATE TABLE IF NOT EXISTS analyzed_reviews (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    review_no       TEXT    UNIQUE,
    product_no      TEXT,
    member_id       TEXT,
    review_text     TEXT,
    rating          INTEGER,
    skin_types      TEXT,
    skin_concerns   TEXT,
    satisfaction    INTEGER,
    keywords        TEXT,
    analyzed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
