import React from 'react'

export function RatingBadge({ rating = '' }) {
    const cls = {
        'Strong Buy': 'badge-strong-buy',
        'Buy': 'badge-buy',
        'Hold': 'badge-hold',
        'Reduce': 'badge-reduce',
        'Avoid': 'badge-avoid',
    }[rating] || 'badge-hold'

    return <span className={`badge ${cls}`}>{rating}</span>
}

export function Loading({ text = 'Loading...' }) {
    return (
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
            <div className="spinner" />
            <p style={{ marginTop: 16, color: 'var(--text-muted)', fontSize: '0.9rem' }}>{text}</p>
        </div>
    )
}

export function ErrorAlert({ message }) {
    return (
        <div className="alert alert-error">
            <span>⚠️</span>
            <span>{message}</span>
        </div>
    )
}

export function SectionHeader({ icon, title }) {
    return (
        <div className="section-header">
            {icon && <span>{icon}</span>}
            <h2>{title}</h2>
        </div>
    )
}

export function ScoreBar({ score, max = 100 }) {
    const pct = Math.min(100, (score / max) * 100)
    const color = pct >= 70 ? 'var(--success)' : pct >= 45 ? 'var(--warning)' : 'var(--danger)'
    return (
        <div className="score-bar-wrap">
            <div className="score-bar">
                <div className="score-bar-fill" style={{ width: `${pct}%`, background: color }} />
            </div>
            <span className="score-num">{typeof score === 'number' ? score.toFixed(0) : score}</span>
        </div>
    )
}

export function formatCurrency(n) {
    if (!n && n !== 0) return '—'
    if (Math.abs(n) >= 1e12) return `$${(n / 1e12).toFixed(1)}T`
    if (Math.abs(n) >= 1e9) return `$${(n / 1e9).toFixed(1)}B`
    if (Math.abs(n) >= 1e6) return `$${(n / 1e6).toFixed(1)}M`
    if (Math.abs(n) >= 1e3) return `$${(n / 1e3).toFixed(1)}K`
    return `$${n.toFixed(2)}`
}

export function formatPct(n, digits = 1) {
    if (n == null) return '—'
    const v = parseFloat(n).toFixed(digits)
    return `${v >= 0 ? '+' : ''}${v}%`
}

export function ColoredPct({ value }) {
    if (value == null) return <span style={{ color: 'var(--text-muted)' }}>—</span>
    const cls = value >= 0 ? 'text-success' : 'text-danger'
    return <span className={cls}>{formatPct(value)}</span>
}
