CREATE INDEX IF NOT EXISTS idx_embeddings_book_model ON embeddings (book_id, model_name);
CREATE INDEX IF NOT EXISTS idx_embeddings_vec_ivfflat ON embeddings USING ivfflat (embeddings vector_cosine_ops) WITH (lists = 50);
ANALYZE embeddings;