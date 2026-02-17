import os
import psycopg
import numpy as np
from dotenv import load_dotenv
from pathlib import Path
from requests import get
from sentence_transformers import SentenceTransformer

load_dotenv()

def get_conn():
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    db = os.getenv("POSTGRES_DB", "book_ai")
    user = os.getenv("POSTGRES_USER", "book_ai")
    password = os.getenv("POSTGRES_PASSWORD")
    if not password:
        raise ValueError("POSTGRES_PASSWORD is not set in environment variables")
    return psycopg.connect(host=host, port=port, dbname=db, user=user, password=password)

def vec_to_pgvector_str(v: np.ndarray) -> str:
    return "[" + ",".join(f"{x:.6f}" for x in v.tolist()) + "]"

def main():
    BOOK_ID = int(os.getenv("BOOK_ID", "6"))
    MODEL_NAME = os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    BATCH = int(os.getenv("EMBED_BATCH", "64"))

    print(f"[INFO] Loading model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    dim = model.get_sentence_embedding_dimension()
    print(f"[INFO] embedding dim = {dim} (DB vector dim = 384)")

    with get_conn() as conn_r, get_conn() as conn_w:
        with conn_w.cursor() as cur_w:
            
            with conn_r.cursor() as cur_r:
                cur_r.execute("select count(*) from chunks where book_id = %s", (BOOK_ID,))
                total = cur_r.fetchone()[0]
                print(f"[INFO] Total chunks: {total}")
                if total == 0:
                    raise RuntimeError(f"No chunks found for book_id={BOOK_ID}")

            inserted = 0
            buf_ids, buf_txt = [], []

            def flush():
                nonlocal inserted, buf_ids, buf_txt
                if not buf_ids:
                    return

                vecs = model.encode(
                    buf_txt,
                    batch_size=min(32, len(buf_txt)),
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                )

                rows = []
                for chunk_id, v in zip(buf_ids, vecs):
                    rows.append((BOOK_ID, chunk_id, MODEL_NAME, vec_to_pgvector_str(v)))


                cur_w.executemany(
                    """
                    insert into embeddings (book_id, chunk_id, model_name, embeddings)
                    values (%s, %s, %s, %s::vector)
                    on conflict (chunk_id, model_name) do nothing
                    """,
                    rows,
                )
                conn_w.commit()  

                inserted += len(rows)
                print(f"[OK] inserted {inserted}/{total}")

                buf_ids, buf_txt = [], []


            with conn_r.cursor(name="chunk_stream") as stream:
                stream.itersize = BATCH
                stream.execute(
                    "select chunk_id, chunk_text from chunks where book_id=%s order by chunk_id;",
                    (BOOK_ID,),
                )

                for chunk_id, chunk_text in stream:
                    buf_ids.append(chunk_id)
                    buf_txt.append(chunk_text)
                    if len(buf_ids) >= BATCH:
                        flush()

            flush()

if __name__ == "__main__":
    main()