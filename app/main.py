from __future__ import annotations

from fastapi import FastAPI

from app.api.routes_products import router as products_router
from app.api.routes_review import router as review_router

app = FastAPI(title="Product Automation Pipeline", version="0.1.0")
app.include_router(products_router)
app.include_router(review_router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
