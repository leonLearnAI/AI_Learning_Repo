import json
import os
from pathlib import Path
from typing import List, Dict

import psycopg
from dotenv import load_dotenv


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

def normalize_text(s: str) -> str:

    # keep the paragraph breaks and remove the spaces at each end of lines
    lines = [ln.strip() for ln in s.splitlines()]
    out = []
    blank = 0
    for ln in lines:
        if ln == "":
            blank += 1
            if blank <= 1:
                out.append(ln)
        else:
            blank = 0
            out.append(ln)
    return "\n".join(out).strip()

def split_paragraphs(text: str) -> List[str]:

    parts = [p.strip() for p in text.split("\n\n")]
    return [p for p in parts if p]

def make_chunks(paragraphs: List[str], chunk_size: int = 1200, overlap: int = 200) -> List[Dict]:
    chunks = []
    buf = ""
    start_para = 0
    i = 0

    while i < len(paragraphs):
        if not buf:
            start_para = i

        candidate = (buf + ("\n\n" if buf else "") + paragraphs[i]).strip()

        if len(candidate) <= chunk_size:
            buf = candidate
            i += 1
            continue

        # ✅ FIX 1: 处理“单段就超过 chunk_size 且 buf 为空”的情况，否则会死循环
        if not buf:
            long_p = paragraphs[i]
            part = long_p[:chunk_size]
            rest = long_p[chunk_size:].strip()

            chunks.append({
                "chunk_text": part,
                "start_para": i,
                "end_para": i,
                "char_len": len(part),
            })

            if rest:
                paragraphs[i] = rest  # 继续切同一段的剩余部分，但这次会变短
            else:
                i += 1               # 这一段刚好切完，推进 i
            continue

        # ✅ 原逻辑：buf 不为空时才输出 buf
        chunks.append({
            "chunk_text": buf,
            "start_para": start_para,
            "end_para": i - 1,
            "char_len": len(buf),
        })

        keep = ""
        j = i - 1
        while j >= start_para and len(keep) < overlap:
            keep = (paragraphs[j] + ("\n\n" if keep else "") + keep).strip()
            j -= 1

        if keep == buf:
            buf = ""
        else:
            buf = keep

    if buf.strip():
        chunks.append({
            "chunk_text": buf.strip(),
            "start_para": start_para,
            "end_para": len(paragraphs) - 1,
            "char_len": len(buf.strip())
        })

    return chunks

def main():
    BOOK_ID = int(os.getenv("BOOK_ID", "6"))
    chunk_size = int(os.getenv("CHUNK_SIZE", "1200"))
    overlap = int(os.getenv("CHUNK_OVERLAP", "200"))

    # just keep a small preview to avoid memory explosion
    preview_limit = int(os.getenv("PREVIEW_LIMIT", "30"))
    chapter_limit = int(os.getenv("CHAPTER_LIMIT", "0"))  

    out_dir = Path("data/processed/the_count_of_monte_cristo")
    out_dir.mkdir(parents=True, exist_ok=True)

    # usering streaming write to avoid large memory usage
    out_jsonl = out_dir / "chunks_preview.jsonl"
    out_preview = out_dir / "chunks_preview_sample.json"

    with get_conn() as conn:
        with conn.cursor() as cur:
            if chapter_limit and chapter_limit > 0:
                cur.execute(
                    """
                    SELECT chapters_id, chapter_index, chapter_text
                    FROM chapters
                    WHERE book_id = %s
                    ORDER BY chapter_index
                    LIMIT %s
                    """,
                    (BOOK_ID, chapter_limit)
                )
            else:
                cur.execute(
                    """
                    SELECT chapters_id, chapter_index, chapter_text
                    FROM chapters
                    WHERE book_id = %s
                    ORDER BY chapter_index
                    """,
                    (BOOK_ID,)
                )
            chapters = cur.fetchall()

    if chapter_limit and chapter_limit > 0:
        chapters = chapters[:chapter_limit]

    total_chunks = 0
    lens = []
    sample = []

    # for the safe write when the file is done and renamed it and save
    tmp_jsonl = out_jsonl.with_suffix(".jsonl.tmp")
    with tmp_jsonl.open("w", encoding="utf-8") as f:
        for (chapters_id, chapter_index, chapter_text) in chapters:
            clean = normalize_text(chapter_text)
            paras = split_paragraphs(clean)
            ch_chunks = make_chunks(paras, chunk_size=chunk_size, overlap=overlap)

            for idx, c in enumerate(ch_chunks, start=1):
                row = {
                    "book_id": BOOK_ID,
                    "chapters_id": chapters_id,      # chapters_id
                    "chapter_index": chapter_index,
                    "chunk_index": idx,
                    **c
                }
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

                total_chunks += 1
                lens.append(row["char_len"])
                if len(sample) < preview_limit:
                    sample.append(row)

    tmp_jsonl.replace(out_jsonl)

    # stats
    lens_sorted = sorted(lens)
    median = lens_sorted[len(lens_sorted)//2] if lens_sorted else 0

    out_preview.write_text(
        json.dumps(sample, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"[OK] book_id={BOOK_ID} chapters={len(chapters)}")
    print(f"[OK] chunks={total_chunks} chunk_size={chunk_size} overlap={overlap}")
    print(f"[OK] char_len min={min(lens) if lens else 0} median={median} max={max(lens) if lens else 0}")
    print(f"[OK] Output(full, jsonl) -> {out_jsonl}")
    print(f"[OK] Output(sample, json) -> {out_preview}")

    # simple preview print
    for r in sample[:2]:
        preview = r["chunk_text"][:200].replace("\n", " ")
        print("\n---")
        print(f"Ch{r['chapter_index']} Chunk{r['chunk_index']} chars={r['char_len']} paras={r.get('start_para')}..{r.get('end_para')}")
        print(f"preview: {preview}...")

if __name__ == "__main__":
    main()






