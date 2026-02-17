import os
import argparse
from unittest import result
from unittest.mock import DEFAULT
from dotenv import load_dotenv
from sympy import preview

from src.services.retrieval import search_chunks

load_dotenv()

DEFAULT_QUESTION = [
    "Who is Edmond Dantès?",
    "Why was Edmond Dantès imprisoned?",
    "Who is Fernand?",
    "Who is Danglars?",
    "What is the Pharaon?",
    "Where does the story begin?",
    "Who is Abbé Faria?",
    "What is Château d'If?",
    "Who is Mercédès?",
    "What is Monte Cristo?"
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--book-id", type=int, default=int(os.getenv("BOOK_ID", "1")))
    parser.add_argument("--model-name", type=str, default=os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"))
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--preview", type=int, default=200)
    args = parser.parse_args()

    for q in DEFAULT_QUESTION:
        print("\n" + "=" * 80)
        print(f"Q: {q}")
        results = search_chunks(
            book_id=args.book_id,
            query=q,
            model_name=args.model_name,
            top_k=args.top_k,
            preview_chars=args.preview
        )
        for i, r in enumerate(results, start=1):
            text = r["chunk_text"].replace("\n", " ").strip()
            print(f"[{i}] {r['citation']} dist={r['distance']:.6f} len={r['char_len']}")
            print("    " + text + "...")
    print("\n[OK] sanity_search done.")

if __name__ == "__main__":
    main()