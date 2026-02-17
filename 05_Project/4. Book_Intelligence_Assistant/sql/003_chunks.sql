CREATE TABLE IF NOT EXISTS chunks (
    chunk_id serial PRIMARY KEY,
    book_id int not NULL references books(book_id) on DELETE CASCADE,
    chapters_id int not NULL REFERENCES chapters(chapters_id) on DELETE CASCADE,
    chapter_index int not NULL,
    chunk_index int not NULL,
    chunk_text text not NULL,
    start_offset int,
    end_offset int,
    char_len int,
    created_at timestamp default current_timestamp
);
create INDEX if not EXISTS idx_chunks_book_chapter_order on chunks(book_id, chapter_index, chunk_index);