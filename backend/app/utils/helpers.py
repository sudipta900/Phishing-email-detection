import re
from urllib.parse import urlparse

import numpy as np
import torch
from bs4 import BeautifulSoup


URL_PATTERN = re.compile(r"https?://[^\s]+", re.IGNORECASE)


def clean_email_body(text: str) -> str:
    if not text:
        return ""

    stripped_html = BeautifulSoup(text, "html.parser").get_text(" ")
    normalized = re.sub(r"\s+", " ", stripped_html)
    return normalized.strip()


def extract_urls(text: str):
    return URL_PATTERN.findall(text or "")


def extract_url_features(url: str):
    parsed = urlparse(url)
    hostname = parsed.netloc.lower()

    suspicious_tokens = [
        "login",
        "verify",
        "secure",
        "update",
        "account",
        "bank",
        "confirm",
    ]

    digit_ratio = (
        sum(character.isdigit() for character in url) / max(len(url), 1)
    )

    return [
        len(url),
        hostname.count("."),
        int(any(token in url.lower() for token in suspicious_tokens)),
        int("@" in url),
        int("-" in hostname),
        digit_ratio,
    ]


def extract_heuristic_features(text: str):
    lowered = (text or "").lower()

    keywords = [
        "urgent",
        "verify",
        "password",
        "click",
        "suspended",
        "account",
        "bank",
        "otp",
        "security alert",
    ]

    uppercase_ratio = (
        sum(character.isupper() for character in text) / max(len(text), 1)
        if text else 0
    )

    return [
        len(text),
        len(extract_urls(text)),
        sum(keyword in lowered for keyword in keywords),
        lowered.count("!"),
        int("http://" in lowered or "https://" in lowered),
        uppercase_ratio,
    ]


def get_bert_probability(cleaned_text: str, tokenizer, bert_model, device):
    if tokenizer is None or bert_model is None:
        return heuristic_probability(cleaned_text)

    encoded = tokenizer(
        cleaned_text,
        truncation=True,
        padding=True,
        max_length=256,
        return_tensors="pt",
    )

    encoded = {
        key: value.to(device)
        for key, value in encoded.items()
    }

    with torch.no_grad():
        logits = bert_model(**encoded).logits
        probabilities = torch.softmax(logits, dim=1)

    return float(probabilities[0][1].item())


def heuristic_probability(text: str) -> float:
    lowered = (text or "").lower()

    weighted_signals = {
        "urgent": 0.12,
        "verify": 0.14,
        "password": 0.18,
        "click": 0.08,
        "suspended": 0.14,
        "account": 0.06,
        "bank": 0.12,
        "gift": 0.08,
        "winner": 0.12,
        "otp": 0.1,
        "security alert": 0.1,
    }

    score = 0.08

    for token, weight in weighted_signals.items():
        if token in lowered:
            score += weight

    if extract_urls(text):
        score += 0.12

    if lowered.count("!") >= 3:
        score += 0.05

    if re.search(r"\b\d{4,}\b", lowered):
        score += 0.03

    return float(np.clip(score, 0.02, 0.98))
