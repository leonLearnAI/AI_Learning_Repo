from pyexpat import model
from fastapi import APIRouter
from networkx import hits
from pydantic import BaseModel
from sympy import preview

from src.services.retrieval import search_chunks

router = APIRouter()

class AskRequest(BaseModel):
    book_id: int = 1
    query: str
    top_k: int = 5
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    preview_chars: int = 350

@router.post("/ask")
def ask(req: AskRequest):
    
    hits = search_chunks(
        book_id = req.book_id,
        query = req.query,
        model_name = req.model_name,
        top_k = req.top_k,
        preview_chars = req.preview_chars
    )
    return {
        "answer" : f"You asked: {req.query}",
        "top_k": req.top_k,
        "spoiler_model": False,
        "citations": hits
    }

