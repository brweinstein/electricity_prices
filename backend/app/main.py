import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import prices, recommendation

app = FastAPI(title="When Should I Use Electricity?")

frontend_origins = {
    "http://localhost:3000",
    os.getenv("FRONTEND_ORIGIN", "").rstrip("/"),
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin for origin in frontend_origins if origin],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(prices.router, prefix="/api")
app.include_router(recommendation.router, prefix="/api")

@app.get("/")
def root():
    return {"status": "ok"}