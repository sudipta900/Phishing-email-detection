from fastapi import APIRouter

from app.schemas import (
    EmailRequest,
    BatchRequest
)

from app.prediction_pipeline import predict_email

router = APIRouter()

@router.post("/predict")
def predict(request: EmailRequest):

    result = predict_email(request.email)

    return result


@router.post("/batch-predict")
def batch_predict(request: BatchRequest):

    results = []

    for email in request.emails:

        prediction = predict_email(email)

        results.append(prediction)

    return {
        "results": results
    }