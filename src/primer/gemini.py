"""Gemini client for the OSSIF Primer."""

import os
from collections.abc import AsyncIterator

from google import genai
from google.genai import types

MODEL = "gemini-3-flash-preview"

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable not set")
        _client = genai.Client(api_key=api_key)
    return _client


async def stream_chat(
    messages: list[dict], system_prompt: str
) -> AsyncIterator[str]:
    """Stream chat response from Gemini.

    Args:
        messages: List of {"role": "user"|"assistant", "content": str}
        system_prompt: The full system prompt

    Yields:
        Text chunks as they arrive from Gemini.
    """
    client = get_client()

    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=role, parts=[types.Part(text=msg["content"])]
            )
        )

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.7,
        top_p=0.9,
        max_output_tokens=2048,
    )

    response_stream = await client.aio.models.generate_content_stream(
        model=MODEL,
        contents=contents,
        config=config,
    )
    async for chunk in response_stream:
        if chunk.text:
            yield chunk.text
