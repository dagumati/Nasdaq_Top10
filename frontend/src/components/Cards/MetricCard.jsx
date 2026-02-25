import React from 'react'
import clsx from 'clsx'

export default function MetricCard({ label, value, delta, deltaType = 'neutral', icon: Icon, accent }) {
    return (
        <div className="metric-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                <span className="metric-label">{label}</span>
                {Icon && (
                    <span style={{ color: 'var(--text-muted)', opacity: 0.6 }}>
                        <Icon size={16} />
                    </span>
                )}
            </div>
            <div className="metric-value" style={accent ? { background: accent, WebkitBackgroundClip: 'text', backgroundClip: 'text' } : {}}>
                {value}
            </div>
            {delta && (
                <div className={clsx('metric-delta', deltaType)}>{delta}</div>
            )}
        </div>
    )
}
