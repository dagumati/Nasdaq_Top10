import React, { useState } from 'react'
import MetricCard from '../components/Cards/MetricCard.jsx'
import { Loading, ErrorAlert, SectionHeader, formatCurrency, ColoredPct } from '../components/Cards/SharedUI.jsx'
import { useApi } from '../hooks/useApi.js'
import { dcaApi } from '../services/api.js'
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, Legend, AreaChart, Area
} from 'recharts'

const SCENARIO_COLORS = { 'Conservative (6%)': '#74b9ff', 'Moderate (10%)': '#667eea', 'Aggressive (14%)': '#764ba2', 'Optimistic (18%)': '#ff6b6b' }

const DEFAULT_PORTFOLIO = [
    { ticker: 'VTI', weight: 0.35 },
    { ticker: 'QQQ', weight: 0.20 },
    { ticker: 'VWO', weight: 0.15 },
    { ticker: 'BND', weight: 0.15 },
    { ticker: 'GLD', weight: 0.10 },
    { ticker: 'INDA', weight: 0.05 },
]

export default function DCASimulator() {
    const [budget, setBudget] = useState(200)
    const [years, setYears] = useState(10)
    const [balance, setBalance] = useState(0)
    const [startDate, setStart] = useState('2020-01-01')
    const [endDate, setEnd] = useState('2024-12-31')
    const [portfolio, setPortfolio] = useState(DEFAULT_PORTFOLIO)

    const { data: scenarios, loading: projLoading, error: projErr, execute: runScenarios } = useApi(dcaApi.scenarios)
    const { data: simResult, loading: simLoading, error: simErr, execute: runSim } = useApi(dcaApi.simulate)

    const runProjection = () => runScenarios({ weekly_contribution: budget, years, existing_balance: balance })
    const runBacktest = () => {
        const tickers = portfolio.map(p => p.ticker)
        const weights = portfolio.map(p => p.weight)
        runSim(tickers, weights, budget, startDate, endDate)
    }

    const updateWeight = (idx, val) => {
        const updated = portfolio.map((p, i) => i === idx ? { ...p, weight: +val } : p)
        setPortfolio(updated)
    }
    const addRow = () => setPortfolio(p => [...p, { ticker: '', weight: 0.05 }])
    const removeRow = idx => setPortfolio(p => p.filter((_, i) => i !== idx))

    // Projection chart data
    const scenarioNames = scenarios ? Object.keys(scenarios) : []
    const projChartData = scenarioNames.length > 0
        ? scenarios[scenarioNames[0]].projections.map((p, i) => {
            const pt = { year: p.year, contributions: p.total_contributions }
            scenarioNames.forEach(name => {
                pt[name] = scenarios[name].projections[i]?.portfolio_value
            })
            return pt
        })
        : []

    // Backtest history chart
    const btHistory = simResult?.weekly_history || []
    const btChartData = btHistory.filter((_, i) => i % 4 === 0).map(w => ({
        date: w.date.slice(0, 7),
        value: w.portfolio_value,
        invested: w.total_invested,
    }))

    return (
        <div>
            <div className="page-header">
                <h1>📈 DCA Simulator</h1>
                <p>Simulate dollar-cost averaging with historical data or project future growth. Harness the power of consistent weekly investing — even with $50/week, compound growth adds up significantly.</p>
            </div>

            {/* Budget controls */}
            <div className="card" style={{ marginBottom: 24 }}>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 24, alignItems: 'flex-end' }}>
                    <div style={{ flex: 1, minWidth: 200 }}>
                        <label className="form-label">Weekly Contribution: <strong style={{ color: 'var(--accent)' }}>${budget}</strong></label>
                        <input type="range" min={50} max={500} step={25} value={budget} onChange={e => setBudget(+e.target.value)} />
                    </div>
                    <div style={{ flex: 1, minWidth: 200 }}>
                        <label className="form-label">Projection Years: <strong style={{ color: 'var(--accent)' }}>{years}</strong></label>
                        <input type="range" min={1} max={30} value={years} onChange={e => setYears(+e.target.value)} />
                    </div>
                    <div style={{ minWidth: 160 }}>
                        <label className="form-label">Existing Balance ($)</label>
                        <input className="form-control" type="number" min={0} value={balance} onChange={e => setBalance(+e.target.value)} style={{ width: 160 }} />
                    </div>
                    <button className="btn btn-primary" onClick={runProjection} disabled={projLoading}>
                        {projLoading ? '⏳ Projecting...' : '📈 Project Growth'}
                    </button>
                </div>
            </div>

            {projLoading && <Loading text="Calculating compound growth..." />}
            {projErr && <ErrorAlert message={projErr} />}

            {scenarios && (
                <>
                    <SectionHeader icon="🔮" title={`Compound Growth — $${budget}/week over ${years} years`} />

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, marginBottom: 20 }}>
                        {scenarioNames.map(name => {
                            const d = scenarios[name]
                            const growth = d.total_growth
                            return (
                                <div key={name} style={{
                                    background: 'rgba(102,126,234,0.06)',
                                    border: `1px solid ${SCENARIO_COLORS[name]}40`,
                                    borderRadius: 'var(--radius-lg)', padding: 16, textAlign: 'center'
                                }}>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>{name}</div>
                                    <div style={{ fontSize: '1.5rem', fontWeight: 700, color: SCENARIO_COLORS[name] }}>{formatCurrency(d.final_value)}</div>
                                    <div style={{ fontSize: '0.78rem', color: 'var(--success)', marginTop: 4 }}>+{formatCurrency(growth)} growth</div>
                                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 2 }}>{((growth / d.total_contributions) * 100).toFixed(0)}% return</div>
                                </div>
                            )
                        })}
                    </div>

                    <div className="card" style={{ height: 400 }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={projChartData}>
                                <CartesianGrid strokeDasharray="4 4" stroke="var(--border)" />
                                <XAxis dataKey="year" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} label={{ value: 'Year', position: 'insideBottom', offset: -4, fill: 'var(--text-muted)', fontSize: 12 }} />
                                <YAxis tickFormatter={v => formatCurrency(v)} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} width={80} />
                                <Tooltip formatter={(v, n) => [formatCurrency(v), n]}
                                    contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-primary)' }} />
                                <Legend wrapperStyle={{ color: 'var(--text-secondary)', fontSize: 12 }} />
                                <Line dataKey="contributions" name="Total Contributions" stroke="rgba(255,255,255,0.25)" strokeDasharray="6 3" dot={false} strokeWidth={2} />
                                {scenarioNames.map(name => (
                                    <Line key={name} dataKey={name} stroke={SCENARIO_COLORS[name]} strokeWidth={2.5} dot={false} />
                                ))}
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </>
            )}

            {/* ── Historical DCA Backtest ── */}
            <SectionHeader icon="⏪" title="Historical DCA Backtest" />
            <div className="card" style={{ marginBottom: 24 }}>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'flex-end' }}>
                    <div>
                        <label className="form-label">Start Date</label>
                        <input className="form-control" type="date" value={startDate} onChange={e => setStart(e.target.value)} style={{ width: 160 }} />
                    </div>
                    <div>
                        <label className="form-label">End Date</label>
                        <input className="form-control" type="date" value={endDate} onChange={e => setEnd(e.target.value)} style={{ width: 160 }} />
                    </div>
                    <button className="btn btn-primary" onClick={runBacktest} disabled={simLoading}>
                        {simLoading ? '⏳ Simulating...' : '⏪ Run Backtest'}
                    </button>
                </div>

                {/* Portfolio editor */}
                <div style={{ marginTop: 20 }}>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 10 }}>Portfolio Weights</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                        {portfolio.map((p, i) => (
                            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                <input className="form-control" placeholder="TICK" value={p.ticker}
                                    onChange={e => setPortfolio(prev => prev.map((x, j) => j === i ? { ...x, ticker: e.target.value.toUpperCase() } : x))}
                                    style={{ width: 70, textAlign: 'center', fontFamily: 'monospace', fontSize: '0.85rem' }} />
                                <input className="form-control" type="number" min={0.01} max={1} step={0.05} value={p.weight}
                                    onChange={e => updateWeight(i, e.target.value)}
                                    style={{ width: 70, fontSize: '0.85rem' }} />
                                <button className="btn btn-ghost" style={{ padding: '6px 8px', fontSize: '0.8rem' }} onClick={() => removeRow(i)}>✕</button>
                            </div>
                        ))}
                        <button className="btn btn-ghost" style={{ padding: '8px 12px' }} onClick={addRow}>+ Add</button>
                    </div>
                </div>
            </div>

            {simLoading && <Loading text="Running DCA simulation with real weekly prices..." />}
            {simErr && <ErrorAlert message={simErr} />}

            {simResult && !simLoading && (
                <>
                    <div className="metric-grid">
                        <MetricCard label="Total Invested" value={formatCurrency(simResult.summary?.total_invested)} />
                        <MetricCard label="Final Value" value={formatCurrency(simResult.summary?.final_portfolio_value)}
                            delta={`CAGR: ${simResult.summary?.cagr_pct?.toFixed(1)}%`} deltaType={simResult.summary?.cagr_pct > 0 ? 'positive' : 'negative'} />
                        <MetricCard label="Total Gain" value={formatCurrency(simResult.summary?.total_gain_loss)}
                            delta={`${simResult.summary?.total_return_pct?.toFixed(1)}%`}
                            deltaType={simResult.summary?.total_return_pct > 0 ? 'positive' : 'negative'} />
                        <MetricCard label="Weeks Invested" value={simResult.simulation_period?.total_weeks}
                            delta={`${simResult.simulation_period?.total_years}yr`} />
                    </div>

                    <div className="card" style={{ height: 380, marginTop: 16 }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={btChartData}>
                                <defs>
                                    <linearGradient id="valGrad" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#667eea" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#667eea" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="4 4" stroke="var(--border)" />
                                <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} interval="preserveStartEnd" />
                                <YAxis tickFormatter={v => formatCurrency(v)} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} width={80} />
                                <Tooltip formatter={(v, n) => [formatCurrency(v), n]}
                                    contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-primary)' }} />
                                <Legend wrapperStyle={{ color: 'var(--text-secondary)', fontSize: 12 }} />
                                <Area dataKey="value" name="Portfolio Value" stroke="#667eea" fill="url(#valGrad)" strokeWidth={2.5} dot={false} />
                                <Area dataKey="invested" name="Total Contributed" stroke="rgba(255,255,255,0.25)" fill="none" strokeDasharray="6 3" strokeWidth={2} dot={false} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Holdings breakdown */}
                    {simResult.holdings?.length > 0 && (
                        <>
                            <SectionHeader icon="📋" title="Final Holdings Breakdown" />
                            <div className="table-wrap">
                                <table>
                                    <thead>
                                        <tr><th>Ticker</th><th>Shares</th><th>Avg Cost</th><th>Current Price</th><th>Cost Basis</th><th>Market Value</th><th>Gain/Loss</th><th>Return</th><th>Actual Wt</th></tr>
                                    </thead>
                                    <tbody>
                                        {simResult.holdings.map(h => (
                                            <tr key={h.ticker}>
                                                <td><strong style={{ color: 'var(--accent)', fontFamily: 'monospace' }}>{h.ticker}</strong></td>
                                                <td style={{ fontFamily: 'monospace' }}>{h.total_shares?.toFixed(4)}</td>
                                                <td>${h.avg_cost_per_share?.toFixed(2)}</td>
                                                <td>${h.current_price?.toFixed(2)}</td>
                                                <td>{formatCurrency(h.cost_basis)}</td>
                                                <td style={{ fontWeight: 600 }}>{formatCurrency(h.market_value)}</td>
                                                <td><ColoredPct value={null} /><span style={{ color: h.unrealized_gain >= 0 ? 'var(--success)' : 'var(--danger)', fontSize: '0.85rem' }}>{h.unrealized_gain >= 0 ? '+' : ''}{formatCurrency(h.unrealized_gain)}</span></td>
                                                <td><ColoredPct value={h.return_pct} /></td>
                                                <td>{h.weight_actual?.toFixed(1)}%</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </>
                    )}
                </>
            )}
        </div>
    )
}
