from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import API_TITLE, API_VERSION

from backend.routes.location import (
    router as location_router
)

from backend.routes.risk import (
    router as risk_router
)

from backend.routes.explanation import (
    router as explanation_router
)

from backend.routes.forecast import (
    router as forecast_router
)

from backend.routes.voice import (
    router as voice_router
)


app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=(
        "Jala Raksha groundwater risk assessment API"
    ),
)


# Frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routes
app.include_router(location_router)
app.include_router(risk_router)
app.include_router(explanation_router)
app.include_router(forecast_router)
app.include_router(voice_router)


@app.get("/health")
def health():
    """
    API health check.
    """
    return {
        "status": "ok",
        "service": "Jala Raksha API",
        "version": API_VERSION,
    }