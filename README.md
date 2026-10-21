# Kaleido

Kaleido is a research prototype intended to help readers explore multiple perspectives on a topic.

## Current prototype scope

- React + Vite frontend.
- FastAPI backend.
- Local keyword-overlap retrieval from `backend/data/articles.json`.
- Results grouped using the perspective labels already present in the dataset.

**Important:** this is not yet an AI-generated balanced synthesis, live news search, or automated fact-checker. The included dataset is very small and contains sample/example sources. Expand and verify the dataset before drawing conclusions or presenting it as a reliable research tool.

## Run locally

Prerequisites: Python 3.10+ and Node.js 18+.

### Backend

From the project root:

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API health: http://127.0.0.1:8000/health  
Interactive API docs: http://127.0.0.1:8000/docs

### Frontend

In a second terminal from the project root:

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (usually http://localhost:5173). Vite proxies `/api` requests to the local backend.

## Deploy as a website

### 1. Push this project to GitHub

Review `.gitignore`, then from the project root:

```bash
git status
git add .
git commit -m "Integrate Kaleido frontend and backend"
git push origin main
```

If GitHub has commits not present locally, fetch and reconcile the histories before pushing; do not force-push unless you intentionally want to replace remote history.

### 2. Deploy the backend on Render

- Create a new Web Service connected to this GitHub repository.
- Set Root Directory to `backend`.
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Add environment variable `FRONTEND_ORIGIN` with your final Vercel frontend origin.
- After deployment, verify `/health` and `/docs`.

The included `render.yaml` describes the backend service settings. Depending on Render's blueprint flow, set `FRONTEND_ORIGIN` in the service environment after the frontend URL exists.

### 3. Deploy the frontend on Vercel

- Import the same GitHub repository into Vercel.
- Set Root Directory to `frontend`.
- Framework preset: Vite.
- Build command: `npm run build`.
- Output directory: `dist`.
- Add environment variable `VITE_API_BASE_URL` with the full Render backend origin (no trailing slash), for example `https://kaleido-api.onrender.com`.
- Keep `VITE_USE_MOCK` set to `false` (or unset).
- Redeploy after changing environment variables.

Then update the Render `FRONTEND_ORIGIN` to the exact Vercel site origin and redeploy the backend if needed.

## API

`POST /api/report`

Example body:

```json
{
  "question": "What are the benefits and challenges of solar energy?",
  "scope": "all",
  "depth": 15,
  "hybrid": true,
  "maxPerspectives": "auto"
}
```

`GET /health` returns `{"status":"running"}`.
