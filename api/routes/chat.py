from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/")
def chat_with_bot(request: ChatRequest):
    """API gọi Trợ lý AI (Retail Catalog RAG & Analytics)"""
    try:
        from rag.rag_service import ask_retail_assistant
        result = ask_retail_assistant(request.message)
        return {
            "reply": result.get("reply", "Xin lỗi, tôi không thể trả lời câu hỏi này."),
            "sources": result.get("sources", []),
            "total_found": result.get("total_found", 0),
            "engine": result.get("engine", "OpenAI GPT-4o-mini + Hybrid Vector Search")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
