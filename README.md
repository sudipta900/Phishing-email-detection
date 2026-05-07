# PhishGuard

AI-powered phishing email detection platform using FastAPI, XGBoost, and DistilBERT.

## Features
- Single email phishing analysis
- Batch email analysis
- Ensemble ML prediction
- URL threat analysis
- Threat explanation engine
- Frontend dashboard

## Backend
Run locally:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Frontend
Open `frontend/index.html` in browser or serve with Live Server.

## Docker
```bash
docker-compose up --build
```


## Deployment

### Backend
Run locally:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker-compose up --build
```

### Frontend
Open `frontend/index.html` in browser
or deploy frontend separately using Vercel/Netlify.
