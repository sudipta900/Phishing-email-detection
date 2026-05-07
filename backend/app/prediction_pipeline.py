import numpy as np
import scipy.sparse as sp

from app.model_loader import (
    xgb_text_model,
    xgb_url_model,
    tfidf_vectorizer,
    ensemble_model,
    tokenizer,
    bert_model,
    device
)

from app.utils.helpers import (
    clean_email_body,
    extract_urls,
    extract_url_features,
    extract_heuristic_features,
    get_bert_probability
)

from app.threat_explainer import explain_threats

def predict_email(raw_email_text: str):

    cleaned_text = clean_email_body(raw_email_text)

    tfidf_features = tfidf_vectorizer.transform(
        [cleaned_text]
    )

    heuristic_features = np.array([
        extract_heuristic_features(cleaned_text)
    ])

    combined_features = sp.hstack([
        tfidf_features,
        sp.csr_matrix(heuristic_features)
    ])

    xgb_text_prob = xgb_text_model.predict_proba(
        combined_features
    )[0][1]

    bert_prob = get_bert_probability(
        cleaned_text,
        tokenizer,
        bert_model,
        device
    )

    ensemble_input = np.array([
        [xgb_text_prob, bert_prob]
    ])

    final_prob = ensemble_model.predict_proba(
        ensemble_input
    )[0][1]

    urls = extract_urls(raw_email_text)

    url_score = None

    if urls:

        url_features = np.array([
            extract_url_features(urls[0])
        ])

        url_score = xgb_url_model.predict_proba(
            url_features
        )[0][1]

        final_prob = (
            (final_prob * 0.7)
            + (url_score * 0.3)
        )

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
        "url_score": (
            round(url_score * 100, 2)
            if url_score else None
        ),
        "threats": threats
    }