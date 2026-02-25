import React, { useState, useEffect } from 'react'
import MetricCard from '../components/Cards/MetricCard.jsx'
import { Loading, ErrorAlert, SectionHeader, RatingBadge, formatCurrency, ColoredPct, ScoreBar } from '../components/Cards/SharedUI.jsx'
import { useApi } from '../hooks/useApi.js'
import { portfolioApi } from '../services/api.js'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'

const COLORS = ['#667eea', '#764ba2', '#00d4aa', '#ffd93d', '#ff6b6b', '#74b9ff', '#a29bfe', '#fd79a8', '#55efc4', '#fdcb6e', '#e17055', '#00cec9']

const RISK_COLOR = { High: 'var(--danger)', 'Medium-High': '#ff9a3c', Medium: 'var(--warning)', 'Low-Medium': '#74b9ff', Low: 'var(--success)' }

export default function ModelPortfolios() {
    const [budget, setBudget] = useState(200)
    const [selected, setSelected] = useState(null)

    const { data: list, loading: listLoading, error: listError, execute: fetchList } = useApi(portfolioApi.list)
    const { data: built, loading: building, error: buildError, execute: build, reset } = useApi(portfolioApi.build)

    useEffect(() => { fetchList() }, [])

    const portfolios = list?.portfolios || []

    const handleBuild = async (name) => {
        setSelected(name)
        reset()
        await build(name, budget)
    }

    const holdings = built?.holdings || []
    const pieData = holdings.map(h => ({ name: h.ticker, value: h.weight_pct }))

    return (
        <div>
            <div className="page-header">
                <h1>🏗️ Model Portfolios</h1>
                <p>Four pre-built, research-backed portfolios from conservative income to aggressive innovation. Each holding is analyzed with live market data and scored for quality.</p>
            </div>

            {/* Budget */}
            <div className="card" style={{ marginBottom: 24, display: 'flex', alignItems: 'center', gap: 24, flexWrap: 'wrap' }}>
                <div style={{ flex: 1, minWidth: 220 }}>
                    <label className="form-label">Weekly DCA Budget: <strong style={{ color: 'var(--accent)' }}>${budget}</strong></label>
                    <input type="range" min={50} max={500} step={25} value={budget} onChange={e => { setBudget(+e.target.value); reset() }} />
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.72rem', marginTop: 4 }}>
                        <span>$50/wk</span><span>$500/wk</span>
                    </div>
                </div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                    <div>📅 Monthly: <strong>${(budget * 4).toLocaleString()}</strong></div>
                    <div>📆 Annual: <strong>${(budget * 52).toLocaleString()}</strong></div>
                    <div>🎯 5yr @ 10%: <strong style={{ color: 'var(--success)' }}>{formatCurrency(budget * 52 * 5 * 1.10)}</strong></div>
                </div>
            </div>

            {listLoading && <Loading text="Loading portfolios..." />}
            {listError && <ErrorAlert message={listError} />}

            {/* Portfolio selection cards */}
            {portfolios.length > 0 && (
                <>
                    <SectionHeader icon="📋" title="Choose a Model Portfolio" />
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16, marginBottom: 28 }}>
                        {portfolios.map(p => (
                            <div key={p.name} className="card" style={{
                                cursor: 'pointer',
                                border: selected === p.name ? '1px solid var(--accent)' : '1px solid var(--border)',
                                boxShadow: selected === p.name ? 'var(--shadow-glow)' : 'var(--shadow-sm)',
                            }} onClick={() => handleBuild(p.name)}>
                                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 8 }}>{p.name}</h3>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: 1.5, marginBottom: 12 }}>{p.description}</p>
                                <div style={{ display: 'flex', gap: 12, fontSize: '0.8rem', flexWrap: 'wrap' }}>
                                    <span style={{ color: 'var(--success)' }}>🎯 {p.target_return}</span>
                                    <span style={{ color: RISK_COLOR[p.risk_level] || 'var(--warning)' }}>⚡ {p.risk_level}</span>
                                    <span style={{ color: 'var(--text-muted)' }}>📦 {p.num_holdings} holdings</span>
                                </div>
                                {selected === p.name && (
                                    <div style={{ marginTop: 12, color: 'var(--accent)', fontSize: '0.82rem', fontWeight: 600 }}>✓ Selected — click to refresh</div>
                                )}
                            </div>
                        ))}
                    </div>
                </>
            )}

            {building && <Loading text={`Building ${selected} with live market data...`} />}
            {buildError && <ErrorAlert message={buildError} />}

            {built && !building && (
                <>
                    <SectionHeader icon="📊" title={`${built.portfolio_name} — Live Analysis`} />

                    {/* Portfolio metrics */}
                    <div className="metric-grid">
                        <MetricCard label="Weekly Investment" value={`$${built.total_weekly_investment?.toFixed(2)}`} delta={`$${built.annual_projection?.toLocaleString()}/year`} deltaType="positive" />
                        <MetricCard label="Portfolio Score" value={`${built.portfolio_composite_score?.toFixed(0)}/100`} deltaType="positive" />
                        <MetricCard label="Avg Volatility" value={`${built.avg_volatility?.toFixed(1)}%`} />
                        <MetricCard label="Holdings" value={built.num_holdings} delta={built.risk_level} />
                    </div>

                    {/* 5-year projections */}
                    <div className="grid-3" style={{ marginBottom: 24 }}>
                        {[['Conservative', built['5yr_projection_low'], '~6%'], ['Moderate', built['5yr_projection_mid'], '~10%'], ['Optimistic', built['5yr_projection_high'], '~15%']].map(([label, val, rate]) => (
                            <div key={label} style={{ background: 'rgba(102,126,234,0.06)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: 20, textAlign: 'center' }}>
                                <div style={{ color: 'var(--text-muted)', fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 6 }}>5-Year — {label}</div>
                                <div style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--accent)' }}>{formatCurrency(val)}</div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 4 }}>@ {rate} CAGR</div>
                            </div>
                        ))}
                    </div>

                    {/* Holdings + Pie */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 24, alignItems: 'start' }}>
                        {/* Holdings table */}
                        <div className="table-wrap">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Ticker</th><th>Role</th><th>Weight</th><th>Weekly $</th>
                                        <th>Price</th><th>Score</th><th>Rating</th><th>3M</th><th>Trend</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {holdings.map(h => (
                                        <tr key={h.ticker}>
                                            <td><strong style={{ color: 'var(--accent)', fontFamily: 'monospace' }}>{h.ticker}</strong></td>
                                            <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{h.role}</td>
                                            <td>{h.weight_pct?.toFixed(1)}%</td>
                                            <td style={{ color: 'var(--success)', fontWeight: 600 }}>${h.weekly_amount?.toFixed(2)}</td>
                                            <td style={{ fontFamily: 'monospace' }}>${h.current_price?.toFixed(2)}</td>
                                            <td style={{ minWidth: 100 }}><ScoreBar score={h.composite_score} /></td>
                                            <td><RatingBadge rating={h.rating} /></td>
                                            <td><ColoredPct value={h.return_3m} /></td>
                                            <td style={{ fontSize: '0.78rem', color: h.trend_strength?.includes('Up') ? 'var(--success)' : 'var(--text-muted)' }}>
                                                {h.trend_strength?.includes('Up') ? '▲' : h.trend_strength?.includes('Down') ? '▼' : '→'} {h.trend_strength}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        {/* Pie chart */}
                        <div className="card" style={{ height: 360 }}>
                            <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: 8 }}>Weight Allocation</div>
                            <ResponsiveContainer width="100%" height="90%">
                                <PieChart>
                                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={110}
                                        dataKey="value" nameKey="name" paddingAngle={2}>
                                        {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                                    </Pie>
                                    <Tooltip formatter={(v) => [`${v.toFixed(1)}%`, 'Weight']}
                                        contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-primary)', fontSize: 13 }} />
                                    <Legend iconSize={10} wrapperStyle={{ color: 'var(--text-secondary)', fontSize: 12 }} />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </>
            )}
        </div>
    )
}
