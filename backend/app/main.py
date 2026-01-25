from fastapi import FastAPI

from .ai.router import router as ai_router

app = FastAPI(title="FinWise API")

app.include_router(ai_router)

@app.get("/health")
def health():
    return {"status": "ok"}
