# PhishGuard

PhishGuard now has:

- a static frontend in `frontend/` for Vercel
- a Docker-ready backend at the repo root for Hugging Face Spaces
- fallback heuristic mode so the API can boot even before every trained asset is available

## Project layout

- `frontend/` contains the site you can deploy to Vercel
- `frontend/config.js` controls the backend API URL used by the frontend
- `backend/` contains the FastAPI phishing detection service
- `Dockerfile` at the repo root is for Hugging Face Spaces using Docker

## Frontend API contract

The frontend expects:

- `POST /predict`
- `POST /batch-predict`

Single request:

```json
{ "email": "raw email text" }
```

Batch request:

```json
{ "emails": ["email one", "email two"] }
```

Example response:

```json
{
  "verdict": "PHISHING",
  "confidence": 93.4,
  "xgb_score": 88.2,
  "bert_score": 95.1,
  "url_score": 90.7,
  "threats": [
    {
      "category": "Urgency",
      "matches": ["urgent", "suspended"]
    }
  ],
  "model_mode": "full"
}
```

## Hugging Face Spaces deployment

Use the options shown in your screenshot:

1. Create a new Space.
2. Choose `Docker`.
3. Choose the `Blank` Docker template.
4. Keep hardware as `CPU Basic` unless you need more.
5. Push this repository to that Space.

This repo already includes a root `Dockerfile` that starts:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

### What to upload to the Space

Upload the full repository, not only `backend/`, because the Space uses the root `Dockerfile`.

### Important environment variable for frontend access

In your Hugging Face Space settings, add:

- `ALLOWED_ORIGINS=https://your-vercel-project.vercel.app`

If you want to test from multiple origins, use comma-separated values:

```text
ALLOWED_ORIGINS=https://your-vercel-project.vercel.app,http://127.0.0.1:5500
```

### Health check after deployment

After the Space is live, test:

- `/`
- `/health`
- `/docs`

Your API base URL will look like:

```text
https://your-username-your-space-name.hf.space
```

## Current backend behavior

There are two backend modes:

- `full` means your real model assets loaded successfully
- `fallback` means the API is running with heuristic scoring because model files are missing, empty, or incomplete

You can confirm the active mode at:

- `GET /`
- `GET /health`

## Model files for full mode

For the real ML pipeline to load, these assets need to exist and be valid inside `backend/models/`:

- `xgb_model.pkl`
- `xgb_url_model.pkl`
- `tfidf_vectorizer.pkl`
- `final_ensemble_model.pkl`
- `distilbert_final/` with the Hugging Face model files

If those are not present yet, deployment still works, but the backend will return heuristic predictions in `fallback` mode.

## Connect the frontend to Hugging Face

Once your Space URL is live, update `frontend/config.js`:

```js
window.PHISHGUARD_CONFIG = {
    apiBase: "https://your-username-your-space-name.hf.space"
};
```

## Vercel deployment for frontend

1. Push this repo to GitHub.
2. Import the repo into Vercel.
3. Set the project root directory to `frontend`.
4. Use the `Other` framework preset.
5. Deploy.
6. After your Hugging Face API URL is ready, update `frontend/config.js`.
7. Redeploy Vercel.

## Local backend run

If you want to test locally before pushing to Spaces, use Python 3.11 if possible. This project uses ML packages that are much more reliable on Python 3.11 or 3.12 than on Python 3.13.

### Windows PowerShell

From the repo root:

```powershell
.\start_backend.ps1
```

That script:

- prefers `py -3.11` when available
- creates `backend/.venv/`
- installs missing backend dependencies
- starts `uvicorn` on port `8000`

### Manual run

```bash
cd backend
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Suggested order

1. Deploy the Hugging Face Space first.
2. Confirm `/health` works.
3. Copy the Space URL into `frontend/config.js`.
4. Deploy `frontend/` to Vercel.
5. Test from the live Vercel site.
