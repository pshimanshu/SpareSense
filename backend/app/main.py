from fastapi import FastAPI

app = FastAPI(title="FinWise API")

@app.get("/health")
def health():
    return {"status": "ok"}