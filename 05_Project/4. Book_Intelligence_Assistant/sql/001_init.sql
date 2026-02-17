-- Create tables books: one row per book
CREATE TABLE IF NOT EXISTS books (
    book_id serial PRIMARY KEY,
    title text NOT NULL,
    language text NOT NULL default 'en',
    source text,
    version text,
    created_at timestamp default current_timestamp
);
-- create table chapters: one row per chapter
create TABLE IF NOT EXISTS chapters (
    chapters_id serial PRIMARY KEY,
    book_id int NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
    chapter_index int not NULL,
    chapter_no_text text,
    chapter_title text,
    chapter_text text not NULL,
    start_line int,
    end_line int,
    body_chars int,
    created_at timestamp default current_timestamp
);
CREATE INDEX IF NOT EXISTS idx_chapters_book_order ON chapters(book_id, chapter_index);