from gettext import find
import json
import re
from pathlib import Path
from tkinter.font import ROMAN
from typing import List, Dict, Optional

ROMAN_RE = re.compile(r"^[IVXLCDM]+\.?$", re.IGNORECASE)

TITLE_RE = re.compile(r"^[A-ZÀ-ÖØ-Ý0-9 ,:;'\()\-\.\?!]+$", re.IGNORECASE)

MIN_BODY_CHARS = 500

def is_roman_line(s: str) -> bool:
    s = s.strip()
    return bool(s) and bool(ROMAN_RE.fullmatch(s))

def is_title_line(s: str) -> bool:
    s = s.strip()
    if not s:
        return False
    if not any(c.isalpha() for c in s):
        return False
    return bool(TITLE_RE.fullmatch(s.upper()))

def read_lines(path: Path) -> List[str]:
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()

def find_body_start(lines: List[str]) -> int:
    # when first find "CONTENTS" can be used as the start of the body
    for idx, s in enumerate(lines):
        if s.strip().upper() in {"CONTENTS", "TABLE OF CONTENTS"}:
            return idx
    return 0

def parse_chapters(lines: List[str]) -> List[Dict]:
    chapters_raw: List[dict] = []

    i = find_body_start(lines)
    n = len(lines)
    while i < n - 1:
        line = lines[i].strip()

        if is_roman_line(line):
            k = i + 1
            while k < n and lines[k].strip() == "":
                k += 1
            if k >= n:
                break

            title_candidate = lines[k].strip()

            if is_title_line(title_candidate):
                chapter_no = line.upper().rstrip(".")   # 统一：去掉末尾点
                chapter_title = title_candidate

                start_line = i
                body_start = k + 1

                # 4) 找下一个章头时，同样允许空行
                j = body_start
                while j < n - 1:
                    if is_roman_line(lines[j].strip()):
                        kk = j + 1
                        while kk < n and lines[kk].strip() == "":
                            kk += 1
                        if kk < n and is_title_line(lines[kk].strip()):
                            break
                    j += 1

                end_line = j
                # 5) 修复 typo：rstrip()
                body_lines = [ln.rstrip() for ln in lines[body_start:end_line]]
                body_text = "\n".join(body_lines).strip()

                chapters_raw.append({
                    "chapter_no_text": chapter_no,
                    "chapter_title": chapter_title,
                    "chapter_text": body_text,
                    "start_line": start_line + 1,
                    "end_line": end_line + 1,
                    "body_chars": len(body_text)
                })

                i = end_line
                continue

        i += 1

    chapters = []
    for item in chapters_raw:
        if item["body_chars"] >= MIN_BODY_CHARS:
            chapters.append(item)

    # 6) 统一字段名：你下面打印用的是 chapter_index
    for idx, item in enumerate(chapters, start=1):
        item["chapter_index"] = idx

    return chapters

def main():
    book_txt = Path("data/raw/the_count_of_monte_cristo/book.txt")
    out_dir = Path("data/processed/the_count_of_monte_cristo")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "chapters.json"

    if not book_txt.exists():
        raise FileNotFoundError(f"Cannot find: {book_txt}")

    lines = read_lines(book_txt)
    chapters = parse_chapters(lines)

    out_json.write_text(json.dumps(chapters, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] Parsed chapters: {len(chapters)}")
    print(f"[OK] Output -> {out_json}")

    for c in chapters[:2]:
        preview = c["chapter_text"][:200].replace("\n", " ")
        print("\n---")
        print(f"#{c['chapter_index']} {c['chapter_no_text']} — {c['chapter_title']}")
        print(f"chars={c['body_chars']} lines={c['start_line']}..{c['end_line']}")
        print(f"preview: {preview}...")

if __name__ == "__main__":
    main()