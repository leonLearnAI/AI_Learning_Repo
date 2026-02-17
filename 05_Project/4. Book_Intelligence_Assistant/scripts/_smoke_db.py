import os
import psycopg
from dotenv import load_dotenv
load_dotenv()

def get_conn():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST","localhost"),
        port=int(os.getenv("POSTGRES_PORT","5432")),
        dbname=os.getenv("POSTGRES_DB","book_ai"),
        user=os.getenv("POSTGRES_USER","book_ai"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

with get_conn() as conn:
    with conn.cursor() as cur:
        cur.execute("select book_id, count(*) from chapters group by book_id order by book_id;")
        print(cur.fetchall())