from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MODELS_PATH = BASE_DIR / "models"
BERT_PATH = MODELS_PATH / "distilbert_final"