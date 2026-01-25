from dotenv import load_dotenv
from fastapi import FastAPI

from .ai.router import router as ai_router

# Load local .env if present so developers don't need to manually export vars.
load_dotenv()

app = FastAPI(title="FinWise API")

app.include_router(ai_router)

@app.get("/health")
def health():
    return {"status": "ok"}
