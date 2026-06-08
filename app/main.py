from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="Product Automation Pipeline", version="0.1.0")


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
