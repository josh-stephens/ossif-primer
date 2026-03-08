"""API routes for the OSSIF Primer."""

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .gemini import stream_chat
from .system_prompt import SYSTEM_PROMPT

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@router.get("/health")
async def health():
    return {"status": "ok", "service": "ossif-primer"}


@router.post("/chat")
async def chat(request: ChatRequest):
    async def generate():
        async for chunk in stream_chat(
            messages=[m.model_dump() for m in request.messages],
            system_prompt=SYSTEM_PROMPT,
        ):
            yield f"data: {json.dumps({'text': chunk})}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
