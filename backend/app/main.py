from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import prices, recommendation

app = FastAPI(title="When Should I Use Electricity?")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(prices.router)
app.include_router(recommendation.router)

@app.get("/")
def root():
    return {"status": "ok"}