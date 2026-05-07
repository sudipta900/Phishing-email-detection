from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas import (
    EmailRequest,
    BatchRequest
)

from app.prediction_pipeline import _heuristic_prediction, predict_email

router = APIRouter()

@router.post("/predict")
def predict(request: EmailRequest):
    try:
        result = predict_email(request.email)
    except Exception:
        result = _heuristic_prediction(request.email)
        result["model_mode"] = "fallback"
        result["model_status"] = "Predict route recovered from a backend inference error."

    return JSONResponse(content=result)


@router.post("/batch-predict")
def batch_predict(request: BatchRequest):
    results = []

    for email in request.emails:
        try:
            prediction = predict_email(email)
        except Exception:
            prediction = _heuristic_prediction(email)
            prediction["model_mode"] = "fallback"
            prediction["model_status"] = "Batch route recovered from a backend inference error."
        results.append(prediction)

    return JSONResponse(content={
        "results": results
    })
