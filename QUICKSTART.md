# Quick Start Guide — Global Investment Research Platform v2.0

[![GitHub](https://img.shields.io/badge/GitHub-dagumati%2FNasdaq__Top10-181717?logo=github)](https://github.com/dagumati/Nasdaq_Top10)

---

## Prerequisites

- **Python** 3.9+ (`python3 --version`)
- **Node.js** 18+ (`node --version`)
- **npm** 9+ (`npm --version`)

---

## Option A — Streamlit Dashboard (Quick, no React needed)

```bash
# 1. Clone
git clone https://github.com/dagumati/Nasdaq_Top10.git
cd Nasdaq_Top10

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Launch Streamlit
python -m streamlit run app.py
# → http://localhost:8501
```

---

## Option B — Full React + FastAPI Stack (Recommended)

### Step 1 — Python Backend

```bash
cd Nasdaq_Top10
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Start the API server
uvicorn backend.main:app --reload --port 8000
# → API: http://localhost:8000
# → Docs: http://localhost:8000/api/docs
```

### Step 2 — React Frontend

```bash
# In a new terminal
cd Nasdaq_Top10/frontend
npm install
npm run dev
# → http://localhost:5173
```

### Step 3 — (Optional) Streamlit alongside

```bash
# In a third terminal
cd Nasdaq_Top10
source venv/bin/activate
python -m streamlit run app.py
# → http://localhost:8501
```

---

## Running Tests

### Backend (pytest)

```bash
source venv/bin/activate
pip install -r backend/requirements.txt
cd backend
pytest tests/ -v --tb=short
```

### Frontend (Jest)

```bash
cd frontend
npm test
# or with coverage:
npm test -- --coverage
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'streamlit.cli'` | Use `python -m streamlit run app.py` not `streamlit run` |
| `npm error EACCES` on npm cache | Run: `sudo chown -R $(whoami) ~/.npm` |
| API returns 500 for market data | yfinance is rate-limited; wait 60s and retry |
| Blank charts in React | Ensure backend is running on port 8000 (`/api/health`) |
| CORS error in browser | Set `FRONTEND_URL` env var on backend to match your frontend URL |

---

## Available URLs

| Service | URL | Notes |
|---------|-----|-------|
| React App | http://localhost:5173 | Primary dashboard |
| FastAPI Docs | http://localhost:8000/api/docs | Interactive Swagger UI |
| FastAPI ReDoc | http://localhost:8000/api/redoc | Alternative API docs |
| Streamlit | http://localhost:8501 | Legacy dashboard |
