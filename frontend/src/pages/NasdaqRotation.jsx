import React, { useState } from 'react'
import MetricCard from '../components/Cards/MetricCard.jsx'
import { Loading, ErrorAlert, SectionHeader, formatCurrency, ColoredPct } from '../components/Cards/SharedUI.jsx'
import { useApi } from '../hooks/useApi.js'
import { nasdaqApi } from '../services/api.js'
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, Legend, BarChart, Bar, Cell
} from 'recharts'

const YEARS = Array.from({ length: 25 }, (_, i) => 2000 + i)
const STRATEGIES = ['Full Rebalancing', 'Add-Only']

export default function NasdaqRotation() {
    const [capital, setCapital] = useState(20000)
    const [startYear, setStart] = useState(2018)
    const [endYear, setEnd] = useState(2024)
    const [topN, setTopN] = useState(10)
    const [strategy, setStrategy] = useState('Full Rebalancing')

    const { data, loading, error, execute } = useApi(nasdaqApi.simulate)

    const run = () => {
        if (startYear >= endYear) return alert('Start year must be before end year')
        execute({ initial_capital: capital, start_year: startYear, end_year: endYear, top_n: topN, strategy })
    }

    // Build chart data from quarterly records
    const history = data?.quarterly_records || data?.portfolio_history || []
    const benchmarks = data?.benchmarks || {}
    const summary = data?.summary || data || {}

    const chartData = history.map(q => ({
        date: q.date || q.quarter,
        portfolio: q.portfolio_value || q.value,
    }))

    // Most held stocks
    const holdFreq = data?.holding_frequency || {}
    const topStocks = Object.entries(holdFreq)
        .sort((a, b) => b[1] - a[1]).slice(0, 15)
        .map(([ticker, count]) => ({ ticker, count }))

    return (
        <div>
            <div className="page-header">
                <h1>📊 Nasdaq Rotation Strategy</h1>
                <p>Backtest the quarterly top-N Nasdaq 100 rotation strategy. Each quarter, rotate into the highest market-cap stocks and compare against QQQ and SPY benchmarks.</p>
            </div>

            {/* Configuration */}
            <div className="card" style={{ marginBottom: 24 }}>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 20, alignItems: 'flex-end' }}>
                    <div>
                        <label className="form-label">Initial Capital ($)</label>
                        <input className="form-control" type="number" min={1000} step={1000} value={capital}
                            onChange={e => setCapital(+e.target.value)} style={{ width: 160 }} />
                    </div>
                    <div>
                        <label className="form-label">Start Year</label>
                        <select className="form-control" value={startYear} onChange={e => setStart(+e.target.value)} style={{ width: 110 }}>
                            {YEARS.map(y => <option key={y}>{y}</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="form-label">End Year</label>
                        <select className="form-control" value={endYear} onChange={e => setEnd(+e.target.value)} style={{ width: 110 }}>
                            {YEARS.map(y => <option key={y}>{y}</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="form-label">Top N Stocks: {topN}</label>
                        <input type="range" min={5} max={20} value={topN} onChange={e => setTopN(+e.target.value)} style={{ width: 140 }} />
                    </div>
                    <div>
                        <label className="form-label">Strategy</label>
                        <select className="form-control" value={strategy} onChange={e => setStrategy(e.target.value)} style={{ width: 180 }}>
                            {STRATEGIES.map(s => <option key={s}>{s}</option>)}
                        </select>
                    </div>
                    <button className="btn btn-primary" onClick={run} disabled={loading} style={{ alignSelf: 'flex-end' }}>
                        {loading ? '⏳ Running...' : '▶ Run Simulation'}
                    </button>
                </div>
                <div style={{ marginTop: 12, color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                    ⏱ Note: Multi-year simulations take 30–90 seconds to fetch and process historical market data.
                </div>
            </div>

            {loading && <Loading text={`Running Nasdaq rotation ${startYear}–${endYear}...`} />}
            {error && <ErrorAlert message={error} />}

            {data && !loading && (
                <>
                    {/* Summary metrics */}
                    <div className="metric-grid">
                        <MetricCard label="Initial Capital" value={formatCurrency(capital)} />
                        <MetricCard label="Final Value" value={formatCurrency(summary.final_value || summary.portfolio_value)}
                            delta={`${summary.total_return_pct?.toFixed(1) || 0}% total return`}
                            deltaType={(summary.total_return_pct || 0) > 0 ? 'positive' : 'negative'} />
                        <MetricCard label="CAGR" value={`${summary.cagr?.toFixed(1) || '?'}%`} deltaType="positive" />
                        <MetricCard label="Quarters" value={summary.num_quarters || history.length} delta="Rebalances" />
                    </div>

                    {/* Benchmark comparison */}
                    {benchmarks.qqq && (
                        <div className="grid-2" style={{ marginBottom: 24 }}>
                            {[['QQQ (Nasdaq 100)', benchmarks.qqq], ['SPY (S&P 500)', benchmarks.spy]].map(([name, b]) => b && (
                                <div key={name} style={{ background: 'rgba(102,126,234,0.06)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: 20 }}>
                                    <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: 8 }}>vs {name}</div>
                                    <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
                                        <div><div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Benchmark Return</div>
                                            <div style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-primary)' }}><ColoredPct value={b.total_return_pct} /></div></div>
                                        <div><div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Our Alpha</div>
                                            <div style={{ fontSize: '1.2rem', fontWeight: 600 }}>
                                                <ColoredPct value={(summary.total_return_pct || 0) - (b.total_return_pct || 0)} />
                                            </div></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Portfolio growth chart */}
                    {chartData.length > 0 && (
                        <>
                            <SectionHeader icon="📈" title="Portfolio Growth" />
                            <div className="card" style={{ height: 380 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={chartData}>
                                        <CartesianGrid strokeDasharray="4 4" stroke="var(--border)" />
                                        <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} interval="preserveStartEnd" />
                                        <YAxis tickFormatter={v => formatCurrency(v)} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} width={85} />
                                        <Tooltip formatter={(v, n) => [formatCurrency(v), n]}
                                            contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-primary)' }} />
                                        <Legend wrapperStyle={{ color: 'var(--text-secondary)', fontSize: 12 }} />
                                        <Line dataKey="portfolio" name="Rotation Strategy" stroke="#667eea" strokeWidth={2.5} dot={false} />
                                        {benchmarks.qqq?.history && <Line data={benchmarks.qqq.history} dataKey="value" name="QQQ" stroke="#00d4aa" strokeWidth={2} dot={false} strokeDasharray="5 3" />}
                                        {benchmarks.spy?.history && <Line data={benchmarks.spy.history} dataKey="value" name="SPY" stroke="#ffd93d" strokeWidth={2} dot={false} strokeDasharray="5 3" />}
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </>
                    )}

                    {/* Most held stocks */}
                    {topStocks.length > 0 && (
                        <>
                            <SectionHeader icon="🏆" title="Most Frequently Held Stocks" />
                            <div className="card" style={{ height: 320 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={topStocks} layout="vertical">
                                        <CartesianGrid strokeDasharray="4 4" stroke="var(--border)" horizontal={false} />
                                        <XAxis type="number" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                                        <YAxis type="category" dataKey="ticker" tick={{ fill: 'var(--text-secondary)', fontSize: 12, fontFamily: 'monospace' }} width={50} />
                                        <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-primary)' }} formatter={(v) => [v, 'Quarters Held']} />
                                        <Bar dataKey="count" name="Quarters Held" radius={[0, 4, 4, 0]}>
                                            {topStocks.map((_, i) => <Cell key={i} fill={i < 3 ? '#667eea' : i < 7 ? '#764ba2' : '#4a4a7a'} />)}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </>
                    )}
                </>
            )}
        </div>
    )
}
