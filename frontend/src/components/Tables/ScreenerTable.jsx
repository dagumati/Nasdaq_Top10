import React, { useState } from 'react'
import { RatingBadge, ScoreBar, ColoredPct, formatCurrency } from '../Cards/SharedUI.jsx'
import { ArrowUpDown } from 'lucide-react'

export default function ScreenerTable({ rows = [] }) {
    const [sortKey, setSortKey] = useState('composite_score')
    const [sortDir, setSortDir] = useState('desc')

    const doSort = key => {
        if (key === sortKey) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
        else { setSortKey(key); setSortDir('desc') }
    }

    const sorted = [...rows].sort((a, b) => {
        const av = a[sortKey] ?? 0
        const bv = b[sortKey] ?? 0
        return sortDir === 'asc' ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1)
    })

    const th = (label, key) => (
        <th onClick={() => doSort(key)} style={{ cursor: 'pointer', userSelect: 'none', whiteSpace: 'nowrap' }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
                {label} <ArrowUpDown size={12} />
            </span>
        </th>
    )

    return (
        <div className="table-wrap">
            <table>
                <thead>
                    <tr>
                        {th('Ticker', 'ticker')}
                        {th('Name', 'name')}
                        <th>Category</th>
                        {th('Price', 'current_price')}
                        {th('Score', 'composite_score')}
                        <th>Rating</th>
                        {th('1M', 'return_1m')}
                        {th('3M', 'return_3m')}
                        {th('6M', 'return_6m')}
                        {th('Volatility', 'volatility_30d')}
                        {th('Sharpe', 'sharpe_ratio')}
                        <th>Trend</th>
                    </tr>
                </thead>
                <tbody>
                    {sorted.map(r => (
                        <tr key={r.ticker}>
                            <td><strong style={{ color: 'var(--accent)', fontFamily: 'var(--font-mono)' }}>{r.ticker}</strong></td>
                            <td style={{ maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.name}</td>
                            <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{r.category}</td>
                            <td style={{ fontFamily: 'monospace' }}>${r.current_price?.toFixed(2)}</td>
                            <td style={{ minWidth: 120 }}><ScoreBar score={r.composite_score} /></td>
                            <td><RatingBadge rating={r.rating} /></td>
                            <td><ColoredPct value={r.return_1m} /></td>
                            <td><ColoredPct value={r.return_3m} /></td>
                            <td><ColoredPct value={r.return_6m} /></td>
                            <td style={{ color: 'var(--text-secondary)' }}>{r.volatility_30d?.toFixed(1)}%</td>
                            <td style={{ color: 'var(--text-secondary)' }}>{r.sharpe_ratio?.toFixed(2)}</td>
                            <td style={{ fontSize: '0.8rem' }}>
                                <span style={{ color: r.trend_strength?.includes('Up') ? 'var(--success)' : r.trend_strength?.includes('Down') ? 'var(--danger)' : 'var(--text-muted)' }}>
                                    {r.trend_strength?.includes('Up') ? '▲' : r.trend_strength?.includes('Down') ? '▼' : '→'} {r.trend_strength}
                                </span>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}
