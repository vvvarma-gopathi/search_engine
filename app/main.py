
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.search import router as search_router

load_dotenv()

app = FastAPI(
    title="Talivy Search API",
    description="A stateless internet search agent.",
    version="1.0.0",
)

frontend_url = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(search_router)


@app.get("/")
def root():
    return {"message": "Talivy Search API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
