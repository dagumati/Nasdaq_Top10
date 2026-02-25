import axios from 'axios'

const BASE = '/api'

const api = axios.create({
    baseURL: BASE,
    timeout: 120_000,   // 2 min — market data can be slow
})

// Request interceptor — attach any future auth token
api.interceptors.request.use(config => {
    const token = localStorage.getItem('auth_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
})

// Response interceptor — normalise errors
api.interceptors.response.use(
    res => res.data,
    err => {
        const msg = err.response?.data?.detail || err.message || 'Unknown error'
        return Promise.reject(new Error(msg))
    }
)

// ── Screener ─────────────────────────────────────────────────
export const screenerApi = {
    universes: () => api.get('/screener/universes'),
    run: (universe, topN, tickers) => api.get('/screener/run', {
        params: { universe, top_n: topN, custom_tickers: tickers?.join(',') || undefined }
    }),
    asset: (ticker) => api.get(`/screener/asset/${ticker}`),
}

// ── Recommendations ───────────────────────────────────────────
export const recommendationsApi = {
    weekly: (budget, riskProfile) => api.get('/recommendations/weekly', {
        params: { weekly_budget: budget, risk_profile: riskProfile }
    }),
}

// ── Portfolio ─────────────────────────────────────────────────
export const portfolioApi = {
    list: () => api.get('/portfolio/list'),
    build: (name, weeklyBudget) => api.get('/portfolio/build', {
        params: { name, weekly_budget: weeklyBudget }
    }),
}

// ── DCA ───────────────────────────────────────────────────────
export const dcaApi = {
    project: (params) => api.get('/dca/project', { params }),
    scenarios: (params) => api.get('/dca/scenarios', { params }),
    simulate: (tickers, weights, budget, start, end) =>
        api.get('/dca/simulate', {
            params: {
                tickers: tickers.join(','),
                weights: weights.join(','),
                weekly_budget: budget,
                start_date: start,
                end_date: end,
            }
        }),
}

// ── Nasdaq ────────────────────────────────────────────────────
export const nasdaqApi = {
    simulate: (params) => api.get('/nasdaq/simulate', { params }),
    universe: () => api.get('/nasdaq/universe'),
}

// ── Health ────────────────────────────────────────────────────
export const healthApi = {
    check: () => api.get('/health'),
}

export default api
