# 🚀 Hosting Guide — Global Investment Research Platform

**Deploy the FastAPI backend and React frontend to production.**

> 📦 Repo: [https://github.com/dagumati/Nasdaq_Top10](https://github.com/dagumati/Nasdaq_Top10)

---

## Architecture Overview

```
Browser (React SPA)
    │
    ▼
Frontend Host (Vercel / Netlify)
    │  /api/* proxy
    ▼
Backend Host (Render / Railway / AWS)
    │
    ▼
Yahoo Finance API (yfinance — no key required)
```

---

## Part 1: Backend Hosting

### Option A — Render (Recommended — Free Tier Available)

1. **Create a Render account** at https://render.com

2. **Create a new Web Service**
   - Connect your GitHub repo: `dagumati/Nasdaq_Top10`
   - Build command: `pip install -r backend/requirements.txt && pip install -r requirements.txt`
   - Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Root directory: leave blank (project root)

3. **Environment Variables** (add in Render dashboard):
   ```
   FRONTEND_URL=https://your-frontend.vercel.app
   PYTHON_VERSION=3.11
   ```

4. **Health Check Path**: `/api/health`

5. Your backend will be live at: `https://your-app.onrender.com`

---

### Option B — Railway

1. Go to https://railway.app → New Project → Deploy from GitHub

2. Select `dagumati/Nasdaq_Top10`

3. Set:
   - **Build command**: `pip install -r backend/requirements.txt -r requirements.txt`
   - **Start command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

4. Add environment variables:
   ```
   PORT=8000
   FRONTEND_URL=https://your-frontend.vercel.app
   ```

5. Railway auto-generates a `*.railway.app` domain

---

### Option C — AWS (EC2 or Elastic Beanstalk)

```bash
# EC2 — manual setup
ssh -i your-key.pem ec2-user@your-ec2-ip

# Install Python + dependencies
sudo yum update -y
sudo yum install python3 python3-pip -y
pip3 install -r requirements.txt -r backend/requirements.txt

# Run with gunicorn + uvicorn workers
pip3 install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 --daemon

# Use nginx as reverse proxy
sudo yum install nginx -y
# Configure nginx to proxy :80 → :8000
```

**Elastic Beanstalk:**
```bash
eb init --platform python-3.11 --region us-east-1
eb create global-investor-api
eb setenv FRONTEND_URL=https://your-frontend.vercel.app
```

---

### Option D — Google Cloud Run

```bash
# Build Docker image
docker build -t gcr.io/YOUR_PROJECT/global-investor-api .

# Push
docker push gcr.io/YOUR_PROJECT/global-investor-api

# Deploy
gcloud run deploy global-investor-api \
  --image gcr.io/YOUR_PROJECT/global-investor-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FRONTEND_URL=https://your-frontend.vercel.app
```

Create a `Dockerfile` in the backend:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt backend/requirements.txt ./
RUN pip install -r requirements.txt -r backend/requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## Part 2: Frontend Hosting

### Option A — Vercel (Recommended)

1. Go to https://vercel.com → Import Git Repository

2. Select `dagumati/Nasdaq_Top10`

3. Set:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

4. Add environment variable:
   ```
   VITE_API_BASE_URL=https://your-backend.onrender.com
   ```

5. Your frontend will be live at: `https://your-app.vercel.app`

6. **Update `vite.config.js`** for production — set proxy target to env var:
   ```js
   proxy: {
     '/api': {
       target: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
       changeOrigin: true,
     }
   }
   ```

---

### Option B — Netlify

1. Go to https://netlify.com → New site from Git

2. Set:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`

3. Add `frontend/public/_redirects`:
   ```
   /api/*  https://your-backend.onrender.com/api/:splat  200
   /*      /index.html                                    200
   ```

4. Environment variables:
   ```
   VITE_API_BASE_URL=https://your-backend.onrender.com
   ```

---

### Option C — GitHub Pages (Static Only)

> ⚠️ GitHub Pages doesn't support server-side proxying. You'll need to configure CORS on the backend and call the API directly from the frontend.

```bash
cd frontend
npm run build
# Push the dist folder to gh-pages branch
npx gh-pages -d dist
```

Update `vite.config.js`:
```js
export default defineConfig({
  base: '/Nasdaq_Top10/',   // GitHub repo name
  ...
})
```

---

## Part 3: Environment Variables Reference

### Backend

| Variable | Required | Description |
|----------|----------|-------------|
| `FRONTEND_URL` | Yes | Full URL of the React frontend (for CORS) |
| `PORT` | Auto | Set by hosting platforms |
| `FMP_API_KEY` | Optional | Financial Modeling Prep key for better data |
| `FINNHUB_API_KEY` | Optional | Finnhub API key |
| `POLYGON_API_KEY` | Optional | Polygon.io API key |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API URL |

---

## Part 4: CI/CD Setup (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt -r backend/requirements.txt
      - run: cd backend && pytest tests/ -v --tb=short

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd frontend && npm ci
      - run: cd frontend && npm test -- --watchAll=false --coverage

  deploy-backend:
    needs: test-backend
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Render
        run: |
          curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK_URL }}"

  deploy-frontend:
    needs: test-frontend
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd frontend && npm ci && npm run build
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./frontend
```

**Required Secrets** (add in GitHub → Settings → Secrets):
| Secret | Description |
|--------|-------------|
| `RENDER_DEPLOY_HOOK_URL` | From Render → Settings → Deploy Hooks |
| `VERCEL_TOKEN` | From Vercel → Account → Tokens |
| `VERCEL_ORG_ID` | From Vercel project settings |
| `VERCEL_PROJECT_ID` | From Vercel project settings |

---

## Part 5: Local Development

```bash
# Terminal 1 — Backend (FastAPI)
cd Nasdaq_Top10
source venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
# → http://localhost:8000/api/docs

# Terminal 2 — Frontend (React/Vite)
cd Nasdaq_Top10/frontend
npm install
npm run dev
# → http://localhost:5173

# Terminal 3 — Streamlit (original dashboard — optional)
cd Nasdaq_Top10
source venv/bin/activate
python -m streamlit run app.py
# → http://localhost:8501
```

---

## Quick Deploy Checklist

- [ ] Backend deployed and `/api/health` returns `{"status":"healthy"}`
- [ ] `FRONTEND_URL` set in backend environment
- [ ] Frontend deployed with correct `VITE_API_BASE_URL`
- [ ] API proxy working (try `/api/screener/universes` from browser)
- [ ] CORS confirmed (no browser console errors)
- [ ] GitHub Actions passing on push to main
