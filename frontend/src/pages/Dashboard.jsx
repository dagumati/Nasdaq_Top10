import React, { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Globe, DollarSign, BarChart2, Repeat, TrendingUp, ArrowRight } from 'lucide-react'
import MetricCard from '../components/Cards/MetricCard.jsx'
import { Loading, ErrorAlert, formatCurrency } from '../components/Cards/SharedUI.jsx'
import { useApi } from '../hooks/useApi.js'
import { healthApi } from '../services/api.js'

const FEATURES = [
    {
        to: '/screener',
        icon: '🌍', title: 'Global Screener',
        desc: 'Screen 100+ ETFs & stocks across thematic, regional, and growth universes.',
        color: '#667eea',
    },
    {
        to: '/recommendations',
        icon: '💰', title: 'Weekly Picks',
        desc: 'AI-generated weekly investment recommendations based on your budget and risk profile.',
        color: '#00d4aa',
    },
    {
        to: '/portfolios',
        icon: '🏗️', title: 'Model Portfolios',
        desc: 'Four pre-built portfolios: Global Growth, Conservative, Aggressive, ESG & Impact.',
        color: '#764ba2',
    },
    {
        to: '/dca',
        icon: '📈', title: 'DCA Simulator',
        desc: 'Simulate $100–$400/week recurring investing with historical data and compound growth projections.',
        color: '#ffd93d',
    },
    {
        to: '/nasdaq',
        icon: '📊', title: 'Nasdaq Rotation',
        desc: 'Backtest quarterly top-10 Nasdaq rotation strategy vs QQQ and SPY benchmarks.',
        color: '#ff6b6b',
    },
]

export default function Dashboard() {
    const { data: health, loading, error, execute } = useApi(healthApi.check)

    useEffect(() => { execute() }, [])

    return (
        <div>
            {/* Hero */}
            <div style={{
                background: 'linear-gradient(135deg, rgba(102,126,234,0.12) 0%, rgba(118,75,162,0.08) 100%)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-xl)',
                padding: '40px',
                marginBottom: '32px',
                position: 'relative',
                overflow: 'hidden',
            }}>
                <div style={{
                    position: 'absolute', top: -40, right: -40,
                    width: 280, height: 280,
                    background: 'radial-gradient(circle, rgba(102,126,234,0.15) 0%, transparent 70%)',
                    borderRadius: '50%',
                }} />
                <h1 style={{ fontSize: '2.2rem', fontWeight: 800, marginBottom: 12 }}>
                    🌍 Global Investment Research Platform
                </h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', maxWidth: 620, lineHeight: 1.7, marginBottom: 24 }}>
                    AI-powered research for everyday investors. Analyze global markets, ETFs, and emerging economies.
                    Start with <strong style={{ color: 'var(--accent)' }}>$100–$400/week</strong> using fractional shares and dollar-cost averaging.
                </p>
                <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                    <Link to="/recommendations" className="btn btn-primary">
                        <DollarSign size={16} /> Get This Week's Picks
                    </Link>
                    <Link to="/screener" className="btn btn-secondary">
                        <Globe size={16} /> Explore Markets
                    </Link>
                </div>
            </div>

            {/* API Health */}
            {loading && <Loading text="Checking API status..." />}
            {error && <ErrorAlert message={`API Offline: ${error} — start the FastAPI backend with: uvicorn backend.main:app --reload`} />}
            {health && (
                <div className="alert alert-success" style={{ marginBottom: 24 }}>
                    ✅ Backend API is online — v{health.version}
                </div>
            )}

            {/* Metrics */}
            <div className="metric-grid">
                <MetricCard label="Universes" value="3" delta="Thematic · Global · Growth" deltaType="neutral" />
                <MetricCard label="Assets Tracked" value="150+" delta="ETFs · Stocks · Funds" deltaType="neutral" />
                <MetricCard label="Model Portfolios" value="4" delta="Conservative to Aggressive" deltaType="neutral" />
                <MetricCard label="Min. Weekly DCA" value="$50" delta="Fractional shares supported" deltaType="positive" />
            </div>

            {/* Feature Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 20 }}>
                {FEATURES.map(f => (
                    <Link key={f.to} to={f.to} style={{ textDecoration: 'none' }}>
                        <div className="card" style={{ height: '100%', cursor: 'pointer' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
                                <span style={{
                                    fontSize: '1.6rem', width: 48, height: 48,
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    background: `${f.color}20`,
                                    borderRadius: 'var(--radius-md)',
                                    border: `1px solid ${f.color}30`,
                                }}>
                                    {f.icon}
                                </span>
                                <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>{f.title}</h3>
                            </div>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', lineHeight: 1.6, marginBottom: 16 }}>
                                {f.desc}
                            </p>
                            <div style={{ color: f.color, fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}>
                                Open <ArrowRight size={14} />
                            </div>
                        </div>
                    </Link>
                ))}
            </div>

            {/* Disclaimer */}
            <p style={{ marginTop: 40, color: 'var(--text-muted)', fontSize: '0.78rem', textAlign: 'center', lineHeight: 1.6 }}>
                ⚠️ For educational purposes only. Not financial advice. Past performance does not guarantee future results.
                Always do your own research. <a href="https://github.com/dagumati/Nasdaq_Top10" target="_blank" rel="noopener noreferrer">GitHub ↗</a>
            </p>
        </div>
    )
}
