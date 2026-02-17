import json
import os
from pathlib import Path

from numpy import dot, insert
import psycopg
from dotenv import load_dotenv
from requests import get

load_dotenv()

def get_conn():
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    db = os.getenv("POSTGRES_DB", "book_ai")
    user = os.getenv("POSTGRES_USER", "book_ai")
    password = os.getenv("POSTGRES_PASSWORD")
    if not password:
        raise ValueError("POSTGRES_PASSWORD is not set in environment variables")
    return psycopg.connect(host=host, port= port, dbname=db, user=user, password=password)

def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield line_no, json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_no}: {line}") from e

def main():
    BOOK_ID = int(os.getenv("BOOK_ID", "1"))
    jsonl_path = Path("data/processed/the_count_of_monte_cristo/chunks_preview.jsonl")
    if not jsonl_path.exists():
        raise FileNotFoundError(f"Cannot find: {jsonl_path}")
    batch_size = int(os.getenv("BATCH_SIZE", "1000"))

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"delete from chunks where book_id = %s", (BOOK_ID,))
        conn.commit()

    print(f"[OK] cleared existing chunks for book_id={BOOK_ID}")

    insert_sql = """
        INSERT INTO chunks
            (book_id, chapters_id, chapter_index, chunk_index, chunk_text, start_offset, end_offset, char_len)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    rows = []
    inserted = 0

    with get_conn() as conn:
        with conn.cursor() as cur:
            for line_no, row in iter_jsonl(jsonl_path):
                if int(row["book_id"]) != BOOK_ID:
                    continue
                rows.append(
                    (
                        row["book_id"],
                        row["chapters_id"],
                        row["chapter_index"],
                        row["chunk_index"],
                        row["chunk_text"],
                        row.get("start_para", 0),
                        row.get("end_para", 0),
                        row["char_len"],
                    )
                )

                if len(rows) >= batch_size:
                    cur.executemany(insert_sql, rows)
                    conn.commit()
                    inserted += len(rows)
                    print(f"[OK] inserted {inserted} rows...")
                    rows.clear()
            if rows:
                cur.executemany(insert_sql, rows)
                conn.commit()
                inserted += len(rows)
                print(f"[OK] inserted {inserted} rows...", flush=True)

    print(f"[OK] Finished ingesting chunks for book_id={BOOK_ID}, total inserted={inserted} from {jsonl_path}")

if __name__ == "__main__":
    main()

