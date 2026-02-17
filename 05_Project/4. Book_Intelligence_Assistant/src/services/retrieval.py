import os
from typing import List, Dict, Optional

import numpy as np
import psycopg
from sentence_transformers import SentenceTransformer

#
_MODEL_CACHE: dict[str, SentenceTransformer] = {}

def get_model(model_name: str) -> SentenceTransformer:
    m = _MODEL_CACHE.get(model_name)
    if m is None:
        m = SentenceTransformer(model_name)
        _MODEL_CACHE[model_name] = m
    return m

def get_conn() -> psycopg.Connection:
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

def embed_query(query: str, model_name: str) -> np.ndarray:
    model = get_model(model_name)
    q = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0]
    return q

def search_chunks(
    *,
    book_id: int,
    query: str,
    model_name: str,
    top_k: int = 5,
    preview_chars: int = 350,
) -> List[Dict]:
    q_vec = vec_to_pgvector_str(embed_query(query, model_name))

    # preview_chars > 0 就只取左侧一段；否则取全文
    if preview_chars and preview_chars > 0:
        text_select = "LEFT(c.chunk_text, %s) AS chunk_text"
        params_prefix: tuple = (preview_chars,)
    else:
        text_select = "c.chunk_text AS chunk_text"
        params_prefix = tuple()

    sql = f"""
    SELECT
        c.chunk_id,
        c.chapter_index,
        c.chunk_index,
        c.char_len,
        {text_select},
        (e.embeddings <=> %s::vector) AS distance
    FROM embeddings e
    JOIN chunks c ON c.chunk_id = e.chunk_id
    WHERE e.book_id = %s
      AND e.model_name = %s
    ORDER BY (e.embeddings <=> %s::vector)
    LIMIT %s;
    """

    params = params_prefix + (q_vec, book_id, model_name, q_vec, top_k)

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

    results: List[Dict] = []
    for (chunk_id, chapter_index, chapter_title, chunk_index, char_len, chunk_text, distance) in rows:
        title = (chapter_title or "").replace("\n", " ").strip()
        results.append({
            "chunk_id": chunk_id,
            "chapter_index": chapter_index,
            "chunk_index": chunk_index,
            "char_len": char_len,
            "distance": float(distance),
            "chunk_text": chunk_text or "",
            "citation": f'[Book#{book_id} Ch{chapter_index} "{title}" Ck{chunk_index} | chunk_id={chunk_id}]',
        })
    return results