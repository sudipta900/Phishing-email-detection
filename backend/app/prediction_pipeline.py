import numpy as np
import scipy.sparse as sp

from app.model_loader import (
    MODEL_MODE,
    bert_model,
    device,
    ensemble_model,
    is_full_model_available,
    tfidf_vectorizer,
    tokenizer,
    xgb_text_model,
    xgb_url_model,
)
from app.threat_explainer import explain_threats
from app.utils.helpers import (
    clean_email_body,
    extract_heuristic_features,
    extract_url_features,
    extract_urls,
    get_bert_probability,
    heuristic_probability,
)


def _heuristic_prediction(raw_email_text: str):
    cleaned_text = clean_email_body(raw_email_text)
    threats = explain_threats(raw_email_text)
    urls = extract_urls(raw_email_text)

    bert_prob = heuristic_probability(cleaned_text)
    xgb_text_prob = min(0.99, max(0.01, bert_prob * 0.92 + 0.04))

    url_score = None
    final_prob = (xgb_text_prob + bert_prob) / 2

    if urls:
        first_url_features = extract_url_features(urls[0])
        url_score = min(
            0.99,
            max(0.05, 0.35 + (sum(first_url_features[:4]) / 120)),
        )
        final_prob = (final_prob * 0.7) + (url_score * 0.3)

    confidence = round(final_prob * 100, 2)

    if final_prob >= 0.75:
        verdict = "PHISHING"
    elif final_prob >= 0.45:
        verdict = "SUSPICIOUS"
    else:
        verdict = "SAFE"

    return {
        "verdict": verdict,
        "confidence": confidence,
        "xgb_score": round(xgb_text_prob * 100, 2),
        "bert_score": round(bert_prob * 100, 2),
        "url_score": round(url_score * 100, 2) if url_score is not None else None,
        "threats": threats,
        "model_mode": MODEL_MODE,
    }


def predict_email(raw_email_text: str):
    if not is_full_model_available():
        return _heuristic_prediction(raw_email_text)

    cleaned_text = clean_email_body(raw_email_text)

    tfidf_features = tfidf_vectorizer.transform([cleaned_text])
    heuristic_features = np.array([extract_heuristic_features(cleaned_text)])

    combined_features = sp.hstack([
        tfidf_features,
        sp.csr_matrix(heuristic_features),
    ])

    xgb_text_prob = xgb_text_model.predict_proba(combined_features)[0][1]
    bert_prob = get_bert_probability(
        cleaned_text,
        tokenizer,
        bert_model,
        device,
    )

    ensemble_input = np.array([[xgb_text_prob, bert_prob]])
    final_prob = ensemble_model.predict_proba(ensemble_input)[0][1]

    urls = extract_urls(raw_email_text)
    url_score = None

    if urls:
        url_features = np.array([extract_url_features(urls[0])])
        url_score = xgb_url_model.predict_proba(url_features)[0][1]
        final_prob = (final_prob * 0.7) + (url_score * 0.3)

    confidence = round(final_prob * 100, 2)

    if final_prob >= 0.75:
        verdict = "PHISHING"
    elif final_prob >= 0.45:
        verdict = "SUSPICIOUS"
    else:
        verdict = "SAFE"

    threats = explain_threats(raw_email_text)

    return {
        "verdict": verdict,
        "confidence": confidence,
        "xgb_score": round(xgb_text_prob * 100, 2),
        "bert_score": round(bert_prob * 100, 2),
        "url_score": round(url_score * 100, 2) if url_score is not None else None,
        "threats": threats,
        "model_mode": MODEL_MODE,
    }
