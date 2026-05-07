import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.model_loader import MODEL_MODE, MODEL_STATUS
from app.routes.predict import router as predict_router

app = FastAPI(
    title="PhishGuard API",
    version="1.0.0",
)


def _allowed_origins():
    configured = os.getenv("ALLOWED_ORIGINS", "*")
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router)


@app.get("/")
def root():
    return {
        "message": "PhishGuard API running",
        "model_mode": MODEL_MODE,
        "status": MODEL_STATUS,
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_mode": MODEL_MODE,
        "model_status": MODEL_STATUS,
    }
