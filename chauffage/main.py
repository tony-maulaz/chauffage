"""Unified entrypoint exposing the Homematic IP API and the Vue frontend."""

from __future__ import annotations

import os
from pathlib import Path

import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .backend import api

app = api.app

_default_origins = [
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_CORS_ORIGINS", ",".join(_default_origins)).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIST = Path(__file__).resolve().parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount(
        "/",
        StaticFiles(directory=FRONTEND_DIST, html=True),
        name="frontend",
    )
else:

    @app.get("/", include_in_schema=False)
    async def frontend_placeholder():
        return JSONResponse(
            {
                "message": (
                    "Frontend build not found. Run `npm run build` inside "
                    "`chauffage/frontend` to generate the static files."
                )
            }
        )


if __name__ == "__main__":
    uvicorn.run(
        "chauffage.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )
