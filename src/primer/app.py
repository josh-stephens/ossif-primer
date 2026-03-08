"""FastAPI application for the OSSIF Primer."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    from .gemini import get_client

    get_client()  # Verify API key at startup
    yield


app = FastAPI(title="OSSIF Primer", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://primer.711bf.org", "http://localhost:8420"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


def main():
    import uvicorn

    uvicorn.run(
        "primer.app:app", host="0.0.0.0", port=8420, workers=1
    )
