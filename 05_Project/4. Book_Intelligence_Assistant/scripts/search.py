import os
import argparse
from dotenv import load_dotenv

from src.services.retrieval import search_chunks

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Vector search over book chunks")
    parser.add_argument("--book-id", type=int, default=int(os.getenv("BOOK_ID", "1")))
    parser.add_argument("--model-name", type=str, default=os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"))
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--preview", type=int, default=350)
    parser.add_argument("query", type=str, help="query text")
    args = parser.parse_args()

    print(f"[INFO] book_id={args.book_id}, model={args.model_name}, top-k={args.top_k}, query={args.query}")

    results = search_chunks(
        book_id=args.book_id,
        query=args.query,
        model_name=args.model_name,
        top_k=args.top_k,
        preview_chars=args.preview,
    )

    if not results:
        print("[WARN] No results. Check book_id/model_name/embeddings exist.")
        return

    print("\n=== TOP RESULTS ===")
    for rank, r in enumerate(results, start=1):
        preview_one_line = r["chunk_text"].replace("\n", " ").strip()
        print(f"[{rank}] {r['citation']} dist={r['distance']:.6f} len={r['char_len']}")
        print("    " + preview_one_line + "...")
        print()

if __name__ == "__main__":
    main()