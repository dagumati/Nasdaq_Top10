import React, { useState, useEffect } from 'react'
import { Search, RefreshCw } from 'lucide-react'
import MetricCard from '../components/Cards/MetricCard.jsx'
import ScreenerTable from '../components/Tables/ScreenerTable.jsx'
import { Loading, ErrorAlert, SectionHeader } from '../components/Cards/SharedUI.jsx'
import { useApi } from '../hooks/useApi.js'
import { screenerApi } from '../services/api.js'
import {
    RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer,
    ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Cell,
} from 'recharts'

const UNIVERSES = [
    { value: 'thematic', label: '🎯 Thematic ETFs' },
    { value: 'global_etfs', label: '🌐 Global & Regional ETFs' },
    { value: 'growth_stocks', label: '🚀 Global Growth Stocks' },
    { value: 'custom', label: '✏️ Custom Tickers' },
]

const PALETTE = ['#667eea', '#764ba2', '#00d4aa', '#ffd93d', '#ff6b6b', '#74b9ff', '#fd79a8', '#a29bfe', '#55efc4', '#fdcb6e']

export default function GlobalScreener() {
    const [universe, setUniverse] = useState('thematic')
    const [topN, setTopN] = useState(15)
    const [custom, setCustom] = useState('')
    const { data, loading, error, execute } = useApi(screenerApi.run)
    const { data: universeData, execute: fetchUniverses } = useApi(screenerApi.universes)

    useEffect(() => { fetchUniverses() }, [])

    const run = () => {
        const tickers = universe === 'custom' ? custom.split(',').map(t => t.trim()).filter(Boolean) : undefined
        execute(universe === 'custom' ? 'thematic' : universe, topN, tickers)
    }

    const results = data?.results || []

    // Radar data for top 5
    const radarData = ['fundamental_score', 'momentum_sub_score', 'risk_adjusted_score', 'macro_alignment_score'].map(k => ({
        metric: k.replace('_score', '').replace('_sub', '').replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()),
        ...Object.fromEntries(results.slice(0, 5).map(r => [r.ticker, r[k]]))
    }))

    return (
        <div>
            <div className="page-header">
                <h1>🌍 Global Market Screener</h1>
                <p>Screen global equities, ETFs, and emerging markets. Assets are ranked by a composite score using fundamentals, momentum, risk-adjusted returns, and macro alignment.</p>
            </div>

            {/* Universe info cards */}
            {universeData && (
                <div className="metric-grid" style={{ marginBottom: 24 }}>
                    <MetricCard label="Thematic ETFs" value={universeData.thematic?.total_assets} delta={`${universeData.thematic?.themes?.length} themes`} />
                    <MetricCard label="Global ETFs" value={universeData.global_etfs?.total_assets} delta={`${universeData.global_etfs?.regions?.length} regions`} />
                    <MetricCard label="Growth Stocks" value={universeData.growth_stocks?.total_assets} delta={`${universeData.growth_stocks?.categories?.length} categories`} />
                </div>
            )}

            {/* Controls */}
            <div className="card" style={{ display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'flex-end', marginBottom: 24 }}>
                <div className="form-group" style={{ margin: 0, flex: '1', minWidth: 200 }}>
                    <label className="form-label">Universe</label>
                    <select className="form-control" value={universe} onChange={e => setUniverse(e.target.value)}>
                        {UNIVERSES.map(u => <option key={u.value} value={u.value}>{u.label}</option>)}
                    </select>
                </div>

                <div className="form-group" style={{ margin: 0, width: 180 }}>
                    <label className="form-label">Top N Results: {topN}</label>
                    <input type="range" min={5} max={50} value={topN} onChange={e => setTopN(+e.target.value)} />
                </div>

                {universe === 'custom' && (
                    <div className="form-group" style={{ margin: 0, flex: '2', minWidth: 280 }}>
                        <label className="form-label">Custom Tickers (comma-separated)</label>
                        <input
                            className="form-control"
                            placeholder="e.g. VTI, QQQ, VWO, INDA, SOXX"
                            value={custom}
                            onChange={e => setCustom(e.target.value)}
                        />
                    </div>
                )}

                <button className="btn btn-primary" onClick={run} disabled={loading}>
                    {loading ? <><RefreshCw size={15} className="spin" /> Scanning...</> : <><Search size={15} /> Run Screener</>}
                </button>
            </div>

            {loading && <Loading text={`Analyzing ${universe} universe...`} />}
            {error && <ErrorAlert message={error} />}

            {results.length > 0 && (
                <>
                    {/* Summary metrics */}
                    <div className="metric-grid">
                        <MetricCard label="Assets Screened" value={results.length} />
                        <MetricCard label="Top Score" value={`${results[0]?.composite_score?.toFixed(0)}/100`} delta={results[0]?.ticker} deltaType="positive" />
                        <MetricCard label="Avg Score" value={`${(results.reduce((s, r) => s + r.composite_score, 0) / results.length).toFixed(1)}/100`} />
                        <MetricCard label="Strong Buys" value={results.filter(r => r.rating === 'Strong Buy').length} deltaType="positive" />
                    </div>

                    {/* Table */}
                    <SectionHeader icon="🏆" title={`Top ${results.length} Ranked Assets`} />
                    <ScreenerTable rows={results} />

                    {/* Score breakdown radar (top 5) */}
                    {results.length >= 3 && (
                        <>
                            <SectionHeader icon="📡" title="Score Breakdown — Top 5 Assets" />
                            <div className="card" style={{ height: 360 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <RadarChart data={radarData}>
                                        <PolarGrid stroke="var(--border)" />
                                        <PolarAngleAxis dataKey="metric" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} />
                                        {results.slice(0, 5).map((r, i) => (
                                            <Radar key={r.ticker} name={r.ticker} dataKey={r.ticker}
                                                stroke={PALETTE[i]} fill={PALETTE[i]} fillOpacity={0.1} />
                                        ))}
                                        <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-primary)' }} />
                                    </RadarChart>
                                </ResponsiveContainer>
                            </div>

                            {/* Risk-return scatter */}
                            <SectionHeader icon="🫧" title="Risk vs Return Landscape" />
                            <div className="card" style={{ height: 380 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <ScatterChart>
                                        <CartesianGrid stroke="var(--border)" strokeDasharray="4 4" />
                                        <XAxis dataKey="volatility_30d" name="Volatility %" label={{ value: 'Volatility (30d %)', position: 'insideBottom', offset: -5, fill: 'var(--text-muted)', fontSize: 12 }} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                                        <YAxis dataKey="return_3m" name="3M Return %" label={{ value: '3M Return %', angle: -90, position: 'insideLeft', fill: 'var(--text-muted)', fontSize: 12 }} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                                        <Tooltip
                                            cursor={{ strokeDasharray: '3 3' }}
                                            content={({ active, payload }) => {
                                                if (!active || !payload?.length) return null
                                                const d = payload[0]?.payload
                                                return (
                                                    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: '10px 14px', fontSize: 13 }}>
                                                        <strong style={{ color: 'var(--accent)' }}>{d?.ticker}</strong>
                                                        <div style={{ color: 'var(--text-secondary)' }}>{d?.name}</div>
                                                        <div>Score: <strong>{d?.composite_score?.toFixed(0)}</strong></div>
                                                        <div>Volatility: {d?.volatility_30d?.toFixed(1)}%</div>
                                                        <div>3M Return: {d?.return_3m?.toFixed(1)}%</div>
                                                    </div>
                                                )
                                            }}
                                        />
                                        <Scatter data={results} name="Assets">
                                            {results.map((r, i) => (
                                                <Cell key={r.ticker} fill={PALETTE[i % PALETTE.length]} opacity={0.85} />
                                            ))}
                                        </Scatter>
                                    </ScatterChart>
                                </ResponsiveContainer>
                            </div>
                        </>
                    )}
                </>
            )}

            <style>{`.spin { animation: spin 1s linear infinite; }`}</style>
        </div>
    )
}
