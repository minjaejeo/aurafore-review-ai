import os
import sqlite3
import json
from dotenv import load_dotenv
from db.models import CREATE_REVIEWS_TABLE

load_dotenv()

DB_PATH = os.getenv("DATABASE_URL", "./reviews.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(CREATE_REVIEWS_TABLE)
        conn.commit()


def save_analyzed_review(review: dict):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO analyzed_reviews
              (review_no, product_no, member_id, review_text, rating,
               skin_types, skin_concerns, satisfaction, keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(review.get("review_no", "")),
                str(review.get("product_no", "")),
                review.get("member_id", ""),
                review.get("review_text", ""),
                review.get("rating", 0),
                json.dumps(review.get("skin_types", []), ensure_ascii=False),
                json.dumps(review.get("skin_concerns", []), ensure_ascii=False),
                review.get("satisfaction", 3),
                json.dumps(review.get("keywords", []), ensure_ascii=False),
            ),
        )
        conn.commit()


def save_many_reviews(reviews: list[dict]):
    for review in reviews:
        save_analyzed_review(review)
    print(f"{len(reviews)}개 리뷰 DB 저장 완료")


def _row_to_dict(row: sqlite3.Row) -> dict:
    r = dict(row)
    r["skin_types"] = json.loads(r["skin_types"] or "[]")
    r["skin_concerns"] = json.loads(r["skin_concerns"] or "[]")
    r["keywords"] = json.loads(r["keywords"] or "[]")
    return r


def get_reviews_by_skin_type(skin_type: str, product_no: str = None) -> list[dict]:
    with get_connection() as conn:
        query = "SELECT * FROM analyzed_reviews WHERE skin_types LIKE ?"
        params: list = [f"%{skin_type}%"]
        if product_no:
            query += " AND product_no = ?"
            params.append(product_no)
        query += " ORDER BY analyzed_at DESC"
        return [_row_to_dict(r) for r in conn.execute(query, params).fetchall()]


def get_all_reviews(product_no: str = None) -> list[dict]:
    with get_connection() as conn:
        if product_no:
            rows = conn.execute(
                "SELECT * FROM analyzed_reviews WHERE product_no = ? ORDER BY analyzed_at DESC",
                (product_no,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM analyzed_reviews ORDER BY analyzed_at DESC"
            ).fetchall()
        return [_row_to_dict(r) for r in rows]
