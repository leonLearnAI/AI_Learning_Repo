-- enable vector extension
CREATE extension if not EXISTS vector;
-- create embeddings table
CREATE TABLE if NOT EXISTS embeddings (
    embeddings_id serial PRIMARY KEY,
    book_id int not NULL references books(book_id) on DELETE CASCADE,
    chunk_id int not NULL references chunks(chunk_id) on DELETE CASCADE,
    model_name text not NULL,
    embeddings vector(384) not NULL,
    created_at timestamp default current_timestamp,
    unique(chunk_id, model_name)
);
-- create index on book_id
CREATE INDEX if not EXISTS idx_embeddings_book ON embeddings (book_id);