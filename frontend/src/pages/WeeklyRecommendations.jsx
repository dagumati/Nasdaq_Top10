import React, { useState } from 'react'
import { Zap } from 'lucide-react'
import MetricCard from '../components/Cards/MetricCard.jsx'
import { Loading, ErrorAlert, SectionHeader, RatingBadge, formatCurrency, ColoredPct } from '../components/Cards/SharedUI.jsx'
import { useApi } from '../hooks/useApi.js'
import { recommendationsApi } from '../services/api.js'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'

const COLORS = ['#667eea', '#00d4aa', '#764ba2', '#ffd93d', '#ff6b6b', '#74b9ff', '#fd79a8', '#a29bfe']

export default function WeeklyRecommendations() {
    const [budget, setBudget] = useState(200)
    const [risk, setRisk] = useState('Moderate')
    const { data, loading, error, execute } = useApi(recommendationsApi.weekly)

    const generate = () => execute(budget, risk)

    const recs = data?.recommendations || []
    const metrics = data?.portfolio_metrics || {}

    // Bucket rollup for pie chart
    const bucketMap = {}
    recs.forEach(r => { bucketMap[r.bucket] = (bucketMap[r.bucket] || 0) + r.weekly_amount })
    const pieData = Object.entries(bucketMap).map(([name, value]) => ({ name, value: +value.toFixed(2) }))

    const projected5yr = budget * 52 * 5 * 1.10

    return (
        <div>
            <div className="page-header">
                <h1>💰 Weekly Investment Picks</h1>
                <p>AI-generated weekly recommendations sized for your budget. Set how much you invest each week and your risk tolerance, and get specific buy amounts with fractional share counts.</p>
            </div>

            {/* Controls */}
            <div className="card" style={{ marginBottom: 24 }}>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 24, alignItems: 'flex-end' }}>
                    <div style={{ flex: 1, minWidth: 200 }}>
                        <label className="form-label">Weekly Budget: <strong style={{ color: 'var(--accent)' }}>${budget}</strong></label>
                        <input type="range" min={50} max={500} step={25} value={budget} onChange={e => setBudget(+e.target.value)} />
                        <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: 4 }}>
                            <span>$50</span><span>$500</span>
                        </div>
                    </div>

                    <div style={{ minWidth: 180 }}>
                        <label className="form-label">Risk Profile</label>
                        <div style={{ display: 'flex', gap: 8 }}>
                            {['Conservative', 'Moderate', 'Aggressive'].map(r => (
                                <button key={r} className={`btn ${risk === r ? 'btn-primary' : 'btn-ghost'}`}
                                    style={{ padding: '8px 14px', fontSize: '0.82rem' }}
                                    onClick={() => setRisk(r)}>
                                    {r}
                                </button>
                            ))}
                        </div>
                    </div>

                    <button className="btn btn-primary" onClick={generate} disabled={loading}>
                        {loading ? '⏳ Analyzing...' : <><Zap size={15} /> Generate Picks</>}
                    </button>
                </div>

                {/* Quick projections */}
                <div className="metric-grid" style={{ marginTop: 20 }}>
                    <MetricCard label="Weekly" value={`$${budget}`} delta={`$${budget * 4}/month`} />
                    <MetricCard label="Annual Contribution" value={`$${(budget * 52).toLocaleString()}`} />
                    <MetricCard label="5-Year Projection" value={formatCurrency(projected5yr)} delta="@ 10% CAGR" deltaType="positive" />
                    <MetricCard label="Risk Profile" value={risk} delta="Selected" />
                </div>
            </div>

            {loading && <Loading text="Analyzing global markets for your weekly picks..." />}
            {error && <ErrorAlert message={error} />}

            {recs.length > 0 && (
                <>
                    {/* Portfolio-level metrics */}
                    <div className="metric-grid">
                        <MetricCard label="Positions" value={metrics.num_positions} delta={`${metrics.num_buckets} buckets`} />
                        <MetricCard label="Portfolio Score" value={`${metrics.weighted_composite_score?.toFixed(0)}/100`} deltaType="positive" />
                        <MetricCard label="Avg Volatility" value={`${metrics.weighted_volatility?.toFixed(1)}%`} />
                        <MetricCard label="Diversification" value={`${metrics.diversification_score}/100`} deltaType="positive" />
                    </div>

                    {/* Allocation pie */}
                    <SectionHeader icon="🥧" title="Weekly Allocation" />
                    <div className="card" style={{ height: 340 }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie data={pieData} cx="50%" cy="50%" innerRadius={80} outerRadius={130}
                                    dataKey="value" nameKey="name" paddingAngle={3}>
                                    {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                                </Pie>
                                <Tooltip formatter={(v) => [`$${v.toFixed(2)}`, 'Weekly Amount']}
                                    contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-primary)' }} />
                                <Legend wrapperStyle={{ color: 'var(--text-secondary)', fontSize: 13 }} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Recommendation cards */}
                    <SectionHeader icon="📋" title="Individual Recommendations" />
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                        {recs.map(rec => (
                            <div key={rec.ticker} className="card" style={{ borderLeft: `3px solid var(--accent)` }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
                                    <div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                                            <strong style={{ fontSize: '1.05rem', color: 'var(--accent)', fontFamily: 'monospace' }}>{rec.ticker}</strong>
                                            <RatingBadge rating={rec.rating} />
                                            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>🪣 {rec.bucket}</span>
                                        </div>
                                        <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: 4 }}>{rec.name}</div>
                                        <div style={{ display: 'flex', gap: 16, fontSize: '0.82rem', color: 'var(--text-muted)', flexWrap: 'wrap' }}>
                                            <span>💵 Price: <strong style={{ color: 'var(--text-primary)' }}>${rec.current_price?.toFixed(2)}</strong></span>
                                            <span>📊 {rec.fractional_shares?.toFixed(4)} shares</span>
                                            <span>📈 3M: <ColoredPct value={rec.return_3m} /></span>
                                            <span>🌡️ Vol: {rec.volatility?.toFixed(1)}%</span>
                                            <span>Score: {rec.composite_score?.toFixed(0)}/100</span>
                                        </div>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent)' }}>
                                            ${rec.weekly_amount?.toFixed(2)}
                                        </div>
                                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>per week</div>
                                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{rec.allocation_pct?.toFixed(1)}% of budget</div>
                                    </div>
                                </div>
                                <p style={{ marginTop: 10, paddingTop: 10, borderTop: '1px solid var(--border)', fontSize: '0.83rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                                    💡 {rec.reason}
                                </p>
                            </div>
                        ))}
                    </div>

                    <p style={{ marginTop: 28, color: 'var(--text-muted)', fontSize: '0.78rem', textAlign: 'center' }}>
                        ⚠️ Educational purposes only. Not financial advice. Always do your own research.
                    </p>
                </>
            )}
        </div>
    )
}
