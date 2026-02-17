import os
import re
from collections import Counter
from typing import List, Tuple, Optional

import psycopg
from dotenv import load_dotenv

load_dotenv()

NAME_RE = re.compile(
    r"\b(?:"
    r"(?:Mr|Mrs|Miss|Monsieur|Madame|M|Mme|Abbé|Count|Countess|Captain|Doctor|Dr|Baron|Marquis|Duke)\.?\s+"
    r")?"
    r"[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿA-ZÀ-ÖØ-Þ'’\-]+"
    r"(?:\s+[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿA-ZÀ-ÖØ-Þ'’\-]+){0,2}"
    r"\b"
)

STOP = {s.upper() for s in {
    "I","He","She","They","We","You",
    "The","A","An","And","But","Or",
    "Chapter","Contents","Book","Volume",
    "Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday",
    "January","February","March","April","May","June","July",
    "August","September","October","November","December",
    "Mr", "Mrs", "Miss", "Monsieur", "Madame", "M", "Mme", "Abbé",
    "Count", "Countess", "Captain", "Doctor", "Dr", "Baron", "Marquis", "Duke",

    # ===== Common dialogue fillers / single-word noise (from your Top30 + typical novel noise) =====
    "Yes", "No", "Well", "So", "As", "Ah", "Oh", "Come", "In", "If", "At", "My",
    "This", "That", "It", "What", "Here", "There", "Now", "Then",
    "Why", "How", "When", "Where", "Who", "Which",
    "That's", "That's", "Dont", "Don't", "Don't",
    "You're", "You're", "Youre",
    "Not", "All", "Let", "However", "After",
    # ===== Common capitalized words that often appear as false positives =====
    "Sir", "Madam", "Lord", "Lady", "Father", "Mother", "Brother", "Sister",
    "God", "Heaven", "Hell","His", "Do", "Don't", "To", "That's", "By", " All", " Paris", "Have", "Let"

    # ===== Book structure words / headings (you already have some; keep them together) =====
    "Chapter", "CHAPTER", "Contents", "CONTENTS", "Book", "BOOK", "Volume", "VOLUME",
    "Part", "PART", "Section", "SECTION",

    # ===== Days / months (you already have; keep them together) =====
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
}}


def get_conn() -> psycopg.Connection:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    db = os.getenv("POSTGRES_DB", "book_ai")
    user = os.getenv("POSTGRES_USER", "book_ai")
    password = os.getenv("POSTGRES_PASSWORD")
    if not password:
        raise ValueError("POSTGRES_PASSWORD is not set")
    return psycopg.connect(host=host, port=port, dbname=db, user=user, password=password)

def normalize_name(s: str) -> str:
    s = (s or "").strip()
    s = s.strip(" ,.;:!?\"'()[]{}")
    s = re.sub(r"\s+", " ", s)
    return s

def extract_candidates(text: str) -> List[str]:
    cands: List[str] = []
    for m in NAME_RE.findall(text or ""):
        name = normalize_name(m)
        if not name:
            continue
        if len(name.split()) > 3:
            continue
        if name.upper() in STOP:
            continue
        if name.isupper() and len(name) <= 6:
            continue
        cands.append(name)
    return cands

def table_exists(cur, table: str) -> bool:
    cur.execute("SELECT to_regclass(%s);", (table,))
    return cur.fetchone()[0] is not None

def get_columns(cur, table: str) -> set[str]:
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema='public' AND table_name=%s
        """,
        (table,),
    )
    return {r[0] for r in cur.fetchall()}

def pick_first(cols: set[str], candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in cols:
            return c
    return None

def safe_ident(name: str) -> str:
    # only allow simple identifiers (no quotes, no spaces)
    if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
        raise ValueError(f"Unsafe identifier: {name}")
    return name

def ensure_unique_index(cur, table: str, col1: str, col2: str, index_name: str):
    # create unique index if not exists (needed for ON CONFLICT(col1, col2))
    t = safe_ident(table)
    c1 = safe_ident(col1)
    c2 = safe_ident(col2)
    ix = safe_ident(index_name)
    cur.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS {ix} ON {t} ({c1}, {c2});")

def clear_book(cur, book_id: int):
    # delete in FK order (mentions -> aliases -> characters) if those tables exist & have book_id
    for t in ("character_mentions", "character_aliases", "characters"):
        if not table_exists(cur, t):
            continue
        cols = get_columns(cur, t)
        if "book_id" in cols:
            cur.execute(f"DELETE FROM {safe_ident(t)} WHERE book_id=%s;", (book_id,))

def main():
    book_id = int(os.getenv("BOOK_ID", "1"))
    chunk_limit = int(os.getenv("CHUNK_LIMIT", "0"))
    min_count = int(os.getenv("MIN_COUNT", "10"))
    max_names = int(os.getenv("MAX_NAMES", "500"))
    clear_first = os.getenv("CLEAR", "0") == "1"

    stream_batch = int(os.getenv("STREAM_BATCH", "200"))
    alias_batch = int(os.getenv("ALIAS_BATCH", "300"))

    print(f"[INFO] book_id={book_id} chunk_limit={chunk_limit} min_count={min_count} max_names={max_names} clear={clear_first}")

    counts: Counter[str] = Counter()

    with get_conn() as conn:
        with conn.cursor() as cur:
            if clear_first:
                clear_book(cur, book_id)
                conn.commit()
                print("[OK] cleared characters/aliases/mentions for this book (if tables exist)")

            # ---- Detect schema: characters table columns ----
            if not table_exists(cur, "characters"):
                raise RuntimeError("Table 'characters' does not exist. Did you run sql/006_characters.sql ?")

            char_cols = get_columns(cur, "characters")

            name_col = pick_first(char_cols, ["canoinical_name", "character_name", "name", "full_name"])
            if not name_col:
                raise RuntimeError(f"Cannot find a name column in characters. Existing columns: {sorted(char_cols)}")

            count_col = pick_first(char_cols, ["mentions_count", "mention_count", "freq", "count"])
            # count_col can be None -> we'll upsert only the name

            # Ensure ON CONFLICT works
            ensure_unique_index(cur, "characters", "book_id", name_col, f"ux_characters_book_{name_col}")
            conn.commit()

            print(f"[INFO] characters.name_col='{name_col}', count_col='{count_col or '<none>'}'")

            # ---- Stream chunks and count names ----
            stream = conn.cursor(name="chunk_stream")
            stream.itersize = stream_batch

            if chunk_limit and chunk_limit > 0:
                stream.execute(
                    """
                    SELECT chunk_text
                    FROM chunks
                    WHERE book_id=%s
                    ORDER BY chunk_id
                    LIMIT %s
                    """,
                    (book_id, chunk_limit),
                )
            else:
                stream.execute(
                    """
                    SELECT chunk_text
                    FROM chunks
                    WHERE book_id=%s
                    ORDER BY chunk_id
                    """,
                    (book_id,),
                )

            seen = 0
            for (chunk_text,) in stream:
                seen += 1
                for nm in extract_candidates(chunk_text or ""):
                    counts[nm] += 1
                if seen % 500 == 0:
                    print(f"[INFO] scanned chunks: {seen}, unique_names={len(counts)}")

            print(f"[OK] scanned chunks: {seen}, unique_names={len(counts)}")

            filtered: List[Tuple[str, int]] = [(n, c) for n, c in counts.items() if c >= min_count]
            filtered.sort(key=lambda x: x[1], reverse=True)
            filtered = filtered[:max_names]
            print(f"[OK] kept candidates: {len(filtered)} (>= {min_count})")

            if not filtered:
                print("[WARN] No candidates passed filters.")
                return

            # ---- Upsert into characters ----
            if count_col:
                sql = f"""
                INSERT INTO characters (book_id, {safe_ident(name_col)}, {safe_ident(count_col)})
                VALUES (%s, %s, %s)
                ON CONFLICT (book_id, {safe_ident(name_col)})
                DO UPDATE SET {safe_ident(count_col)} = EXCLUDED.{safe_ident(count_col)}
                """
                params = [(book_id, n, cnt) for n, cnt in filtered]
            else:
                sql = f"""
                INSERT INTO characters (book_id, {safe_ident(name_col)})
                VALUES (%s, %s)
                ON CONFLICT (book_id, {safe_ident(name_col)})
                DO NOTHING
                """
                params = [(book_id, n) for n, _ in filtered]

            cur.executemany(sql, params)
            conn.commit()
            print("[OK] upserted characters")

            # ---- Insert aliases (optional) ----
            if table_exists(cur, "character_aliases"):
                alias_cols = get_columns(cur, "character_aliases")
                required = {"book_id", "character_id", "alias"}
                if not required.issubset(alias_cols):
                    print(f"[WARN] character_aliases exists but missing columns {required - alias_cols}, skip aliases.")
                else:
                    # detect optional columns
                    norm_col = "norm_alias" if "norm_alias" in alias_cols else None
                    conf_col = "confidence" if "confidence" in alias_cols else None

                    # fetch character_id + name
                    # detect id column in characters table
                    id_col = pick_first(char_cols, ["character_id", "id"])
                    if not id_col:
                        print("[WARN] cannot find character_id column in characters, skip aliases.")
                    else:
                        # batch select to avoid huge ANY list
                        names = [n for n, _ in filtered]
                        total_alias = 0

                        for i in range(0, len(names), alias_batch):
                            batch = names[i:i+alias_batch]
                            cur.execute(
                                f"""
                                SELECT {safe_ident(id_col)}, {safe_ident(name_col)}
                                FROM characters
                                WHERE book_id=%s AND {safe_ident(name_col)} = ANY(%s::text[])
                                """,
                                (book_id, batch),
                            )
                            rows = cur.fetchall()

                            alias_rows = []
                            for cid, nm in rows:
                                if norm_col and conf_col:
                                    alias_rows.append((book_id, cid, nm, nm.lower(), 1.0))
                                elif norm_col and not conf_col:
                                    alias_rows.append((book_id, cid, nm, nm.lower()))
                                elif (not norm_col) and conf_col:
                                    alias_rows.append((book_id, cid, nm, 1.0))
                                else:
                                    alias_rows.append((book_id, cid, nm))

                            if not alias_rows:
                                continue

                            if norm_col and conf_col:
                                ins = """
                                INSERT INTO character_aliases (book_id, character_id, alias, norm_alias, confidence)
                                VALUES (%s, %s, %s, %s, %s)
                                ON CONFLICT DO NOTHING
                                """
                            elif norm_col and not conf_col:
                                ins = """
                                INSERT INTO character_aliases (book_id, character_id, alias, norm_alias)
                                VALUES (%s, %s, %s, %s)
                                ON CONFLICT DO NOTHING
                                """
                            elif (not norm_col) and conf_col:
                                ins = """
                                INSERT INTO character_aliases (book_id, character_id, alias, confidence)
                                VALUES (%s, %s, %s, %s)
                                ON CONFLICT DO NOTHING
                                """
                            else:
                                ins = """
                                INSERT INTO character_aliases (book_id, character_id, alias)
                                VALUES (%s, %s, %s)
                                ON CONFLICT DO NOTHING
                                """

                            cur.executemany(ins, alias_rows)
                            conn.commit()
                            total_alias += len(alias_rows)

                        print(f"[OK] inserted aliases: {total_alias}")
            else:
                print("[INFO] character_aliases table not found, skip aliases.")

    print("[DONE] Step 6.2 complete.")


if __name__ == "__main__":
    main()