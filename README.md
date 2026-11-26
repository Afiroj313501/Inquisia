# Inquisia

**Discover Your Research Interests. Find Your Direction.**

Inquisia is an AI-powered research interest discovery and personalized research recommendation platform for students and early-stage researchers.

## Project Structure

- `backend/` — FastAPI modular monolith API
- `frontend/` — React + TypeScript + Vite + Tailwind CSS client

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run backend tests:

```bash
pytest
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Run frontend tests and build:

```bash
npm test
npm run build
```
