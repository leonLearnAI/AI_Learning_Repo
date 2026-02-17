import json
import os
from pathlib import Path

import psycopg

def get_conn():
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", 5432))
    db = os.getenv("POSTGRES_DB", "book_ai")
    user = os.getenv("POSTGRES_USER", "book_ai")
    password = os.getenv("POSTGRES_PASSWORD", "book_ai_password")
    return psycopg.connect(host=host, port=port, dbname=db, user=user, password=password)

def main():
    chapters_path = Path("data/processed/the_count_of_monte_cristo/chapters.json")
    if not chapters_path.exists():
        raise FileNotFoundError(f"Cannot find: {chapters_path}")
    
    chapters = json.loads(chapters_path.read_text(encoding="utf-8"))

    title = "The Count of Monte Cristo"
    language = "en"
    source = "local file"
    version = "v1.0"

    with get_conn() as conn:
        with conn.cursor() as cur:

# 1. Insert book record
            cur.execute(
                """
                insert into books (title, language, source, version)
                values (%s, %s, %s, %s)
                returning book_id
                """,
                (title, language, source, version)
            )
            book_id = cur.fetchone()[0]
# 2. Insert chapter records
            rows = []
            for c in chapters:
                rows.append(
                    (
                        book_id,
                        c.get("chapter_index"),
                        c.get("chapter_no_text"),
                        c.get("chapter_title"),
                        c.get("chapter_text"),
                        c.get("start_line"),
                        c.get("end_line"),
                        c.get("body_chars")
                    )
                )
            cur.executemany(
                """
                insert into chapters (
                book_id, 
                chapter_index, 
                chapter_no_text, 
                chapter_title,
                chapter_text, 
                start_line, 
                end_line, 
                body_chars)
                values (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                rows
            )
        conn.commit()
    print(f"[OK] Ingested book and book_id= {book_id} chapters= {len(chapters)} into Postgres.")

if __name__ == "__main__":
    main()