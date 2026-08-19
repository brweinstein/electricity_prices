from fastapi import FastAPI
from app.api import prices, recommendation

app = FastAPI(title="When Should I Use Electricity?")

app.include_router(prices.router)
app.include_router(recommendation.router)

@app.get("/")
def root():
    return {"status": "ok"}