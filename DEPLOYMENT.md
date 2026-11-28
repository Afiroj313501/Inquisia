# Deploying Inquisia

Inquisia can be deployed either as **Backend (Render) + Frontend (Vercel)** or on a **single VPS with Docker Compose**.

---

## Option 1: Render (Backend + PostgreSQL) + Vercel (Frontend)

### 1. Backend on Render
1. Push this repository to GitHub.
2. In Render, click **New → Blueprint** and select your repository (uses [`render.yaml`](render.yaml)).
3. Render automatically provisions `inquisia-db` (PostgreSQL), generates a strong `JWT_SECRET_KEY`, and runs `alembic upgrade head && uvicorn app.main:app`.
4. Note your backend URL (e.g. `https://inquisia-api.onrender.com`) and set the remaining env vars in Render:
   - `CORS_ORIGINS`: `["https://your-frontend.vercel.app"]`
   - `GEMINI_API_KEY`: your Google AI Studio key *(optional, for AI Research Briefs / Synthesis / Niche Summary)*
   - `OPENALEX_MAILTO`: your contact email *(optional, enables OpenAlex polite pool)*

> **Note on Render `DATABASE_URL`:** Render's `connectionString` starts with `postgresql://...`. SQLAlchemy 2.0 + `psycopg` works with `postgresql+psycopg://...`. If Render provides `postgresql://`, either update `DATABASE_URL` or ensure `psycopg` dialect is used (`postgresql+psycopg://...`).

### 2. Frontend on Vercel
1. In Vercel, import the same repository and set **Root Directory** to `frontend`.
2. Framework preset: **Vite** (`npm run build`, output `dist`). [`frontend/vercel.json`](frontend/vercel.json) handles React Router SPA rewrites.
3. Add environment variable in Vercel:
   - `VITE_API_BASE_URL`: `https://inquisia-api.onrender.com` *(no trailing slash)*
4. Deploy, then copy your Vercel URL back into Render's `CORS_ORIGINS` JSON array.

---

## Option 2: Single VPS with Docker Compose

1. Create a `.env` file alongside `docker-compose.yml`:
   ```env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=use-a-strong-db-password
   POSTGRES_DB=inquisia
   JWT_SECRET_KEY=replace-with-generated-64-char-secret
   GEMINI_API_KEY=your-gemini-key
   OPENALEX_MAILTO=you@example.com
   ```
2. Launch all services:
   ```bash
   docker compose up -d --build
   ```
3. Put a reverse proxy (Caddy / Nginx / Cloudflare) in front of port `5173` for HTTPS.
