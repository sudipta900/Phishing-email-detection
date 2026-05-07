import pickle
import torch

from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification
)

from app.config import MODELS_PATH, BERT_PATH

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Loading models...")

with open(MODELS_PATH / "xgb_model.pkl", "rb") as f:
    xgb_text_model = pickle.load(f)

with open(MODELS_PATH / "xgb_url_model.pkl", "rb") as f:
    xgb_url_model = pickle.load(f)

with open(MODELS_PATH / "tfidf_vectorizer.pkl", "rb") as f:
    tfidf_vectorizer = pickle.load(f)

with open(MODELS_PATH / "final_ensemble_model.pkl", "rb") as f:
    ensemble_model = pickle.load(f)

tokenizer = DistilBertTokenizer.from_pretrained(BERT_PATH)

bert_model = DistilBertForSequenceClassification.from_pretrained(
    BERT_PATH
)

bert_model.to(device)
bert_model.eval()

print("All models loaded successfully.")