import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = os.getenv("POSTGRES_PORT", "5432")
    postgres_db: str = os.getenv("POSTGRES_DB", "book_ai")
    postgres_user: str = os.getenv("POSTGRES_USER", "dap")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "dap")

    default_top_k: int = int(os.getenv("DEFAULT_TOP_K", 5))
    default_spoiler_model: bool = os.getenv("DEFAULT_SPOILER_MODEL", "false").lower() == "true"

settings = Settings()