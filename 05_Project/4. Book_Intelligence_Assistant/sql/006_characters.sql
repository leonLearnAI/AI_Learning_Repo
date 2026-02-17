CREATE TABLE IF NOT EXISTS characters (
    character_id serial PRIMARY KEY,
    book_id int NOT NULL references books(book_id) on delete cascade,
    canoinical_name text NOT NULL,
    mention_count int default 0,
    chapter_span int default 0,
    created_at timestamp default current_timestamp,
    unique (book_id, canoinical_name)
);
CREATE INDEX IF NOT EXISTS idx_characters_book on characters (book_id);
CREATE index if not EXISTS idx_characters_book_name on characters (book_id, canoinical_name);
CREATE TABLE IF NOT EXISTS character_aliases (
    alias_id serial PRIMARY KEY,
    book_id int NOT NULL references books(book_id) on delete cascade,
    character_id int NOT NULL references characters(character_id) on delete cascade,
    alias text NOT NULL,
    norm_alias text,
    confidence real default 0.0,
    created_at timestamp default current_timestamp,
    unique (character_id, alias)
);
CREATE index if not EXISTS idx_aliases_book on character_aliases (book_id);
CREATE index if not EXISTS idx_aliases_character on character_aliases (character_id);
CREATE index if not EXISTS idx_aliases_book_aliasa on character_aliases (book_id, alias);
CREATE TABLE if NOT EXISTS character_metions (
    mention_id serial PRIMARY KEY,
    book_id int not NULL references books(book_id) on delete cascade,
    character_id int not NULL references characters(character_id) on delete cascade,
    alias_id int not NULL references character_aliases(alias_id) on delete cascade,
    chunk_id int not NULL references chunks(chunk_id) on delete cascade,
    surface_form text not NULL,
    start_offset int,
    end_offset int,
    created_at timestamp default current_timestamp
);
CREATE index if not EXISTS idx_aliases_book_character on character_metions (book_id, character_id);
CREATE index if not EXISTS idx_mentions_chunk on character_metions (chunk_id);
CREATE index if not exists idx_mentions_alias on character_metions (alias_id);