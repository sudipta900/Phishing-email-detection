import pickle
from pathlib import Path

import torch
from transformers import (
    AutoTokenizer,
    DistilBertForSequenceClassification,
)

from app.config import BERT_PATH, MODELS_PATH

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

xgb_text_model = None
xgb_url_model = None
tfidf_vectorizer = None
ensemble_model = None
tokenizer = None
bert_model = None
MODEL_MODE = "fallback"
MODEL_STATUS = "Model assets not found. Using heuristic fallback mode."


def _file_has_content(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0


def _bert_assets_available(path: Path) -> bool:
    required_files = {
        "config.json",
        "model.safetensors",
        "tokenizer_config.json",
    }
    tokenizer_files = {"tokenizer.json", "vocab.txt"}

    return (
        path.exists()
        and all((path / file_name).exists() for file_name in required_files)
        and any((path / file_name).exists() for file_name in tokenizer_files)
    )


def _load_pickle(path: Path):
    with open(path, "rb") as file_obj:
        return pickle.load(file_obj)


def load_models() -> None:
    global xgb_text_model
    global xgb_url_model
    global tfidf_vectorizer
    global ensemble_model
    global tokenizer
    global bert_model
    global MODEL_MODE
    global MODEL_STATUS

    structured_assets = [
        MODELS_PATH / "xgb_model.pkl",
        MODELS_PATH / "xgb_url_model.pkl",
        MODELS_PATH / "tfidf_vectorizer.pkl",
        MODELS_PATH / "final_ensemble_model.pkl",
    ]

    if not all(_file_has_content(path) for path in structured_assets):
        MODEL_MODE = "fallback"
        MODEL_STATUS = "Classic model pickle files are missing or empty. Using heuristic fallback mode."
        return

    try:
        xgb_text_model = _load_pickle(MODELS_PATH / "xgb_model.pkl")
        xgb_url_model = _load_pickle(MODELS_PATH / "xgb_url_model.pkl")
        tfidf_vectorizer = _load_pickle(MODELS_PATH / "tfidf_vectorizer.pkl")
        ensemble_model = _load_pickle(MODELS_PATH / "final_ensemble_model.pkl")
    except Exception as exc:
        MODEL_MODE = "fallback"
        MODEL_STATUS = f"Failed to load pickle models: {exc}"
        return

    if _bert_assets_available(BERT_PATH):
        try:
            tokenizer = AutoTokenizer.from_pretrained(BERT_PATH)
            bert_model = DistilBertForSequenceClassification.from_pretrained(BERT_PATH)
            bert_model.to(device)
            bert_model.eval()
        except Exception as exc:
            tokenizer = None
            bert_model = None
            MODEL_MODE = "fallback"
            MODEL_STATUS = f"Classic models loaded, but BERT assets failed: {exc}"
            return
    else:
        MODEL_MODE = "fallback"
        MODEL_STATUS = "Classic models loaded, but BERT directory is incomplete. Using heuristic fallback mode."
        return

    MODEL_MODE = "full"
    MODEL_STATUS = "All model assets loaded successfully."


def is_full_model_available() -> bool:
    return MODEL_MODE == "full"


load_models()
