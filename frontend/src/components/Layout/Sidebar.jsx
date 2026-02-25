import React from 'react'
import { NavLink } from 'react-router-dom'
import {
    Globe, TrendingUp, DollarSign, BarChart2, Activity, Repeat,
    Github, ChevronRight
} from 'lucide-react'

const NAV_ITEMS = [
    { to: '/', icon: Activity, label: 'Dashboard' },
    { to: '/screener', icon: Globe, label: 'Global Screener' },
    { to: '/recommendations', icon: DollarSign, label: 'Weekly Picks' },
    { to: '/portfolios', icon: BarChart2, label: 'Model Portfolios' },
    { to: '/dca', icon: Repeat, label: 'DCA Simulator' },
    { to: '/nasdaq', icon: TrendingUp, label: 'Nasdaq Rotation' },
]

export default function Sidebar() {
    return (
        <aside className="sidebar">
            {/* Logo */}
            <div className="sidebar-logo">
                <span className="sidebar-logo-icon">🌍</span>
                <div>
                    <div className="sidebar-logo-title">Global Investor</div>
                    <div className="sidebar-logo-sub">AI Research Platform</div>
                </div>
            </div>

            {/* Nav */}
            <nav className="sidebar-nav">
                <div className="sidebar-nav-label">Navigation</div>
                {NAV_ITEMS.map(item => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        end={item.to === '/'}
                        className={({ isActive }) =>
                            `sidebar-link ${isActive ? 'active' : ''}`
                        }
                    >
                        <item.icon size={18} />
                        <span>{item.label}</span>
                        <ChevronRight size={14} className="sidebar-link-arrow" />
                    </NavLink>
                ))}
            </nav>

            {/* Footer */}
            <div className="sidebar-footer">
                <a
                    href="https://github.com/dagumati/Nasdaq_Top10"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="sidebar-link"
                >
                    <Github size={16} />
                    <span>dagumati/Nasdaq_Top10</span>
                </a>
                <div className="sidebar-version">v2.0.0</div>
            </div>

            <style>{`
        .sidebar {
          position: fixed;
          top: 0; left: 0;
          width: var(--sidebar-w);
          height: 100vh;
          background: var(--bg-secondary);
          border-right: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          z-index: 100;
          overflow: hidden;
        }
        .sidebar-logo {
          display: flex; align-items: center; gap: 12px;
          padding: 20px 16px;
          border-bottom: 1px solid var(--border);
          flex-shrink: 0;
        }
        .sidebar-logo-icon   { font-size: 1.6rem; }
        .sidebar-logo-title  { font-size: 0.95rem; font-weight: 700; color: var(--text-primary); }
        .sidebar-logo-sub    { font-size: 0.7rem; color: var(--text-muted); }
        .sidebar-nav         { flex: 1; overflow-y: auto; padding: 12px 8px; }
        .sidebar-nav-label   {
          font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.1em;
          color: var(--text-muted); padding: 8px 10px 4px;
        }
        .sidebar-link {
          display: flex; align-items: center; gap: 10px;
          padding: 10px 12px;
          border-radius: var(--radius-sm);
          color: var(--text-secondary);
          font-size: 0.87rem; font-weight: 500;
          transition: all var(--transition);
          text-decoration: none;
          margin-bottom: 2px;
          position: relative;
        }
        .sidebar-link:hover { background: var(--bg-card); color: var(--text-primary); }
        .sidebar-link.active {
          background: rgba(102,126,234,0.12);
          color: var(--accent);
          font-weight: 600;
        }
        .sidebar-link.active::before {
          content: '';
          position: absolute; left: 0; top: 20%; bottom: 20%;
          width: 3px; border-radius: 0 2px 2px 0;
          background: var(--accent-grad);
        }
        .sidebar-link-arrow { margin-left: auto; opacity: 0; transition: opacity var(--transition); }
        .sidebar-link:hover .sidebar-link-arrow { opacity: 0.5; }
        .sidebar-link.active .sidebar-link-arrow { opacity: 1; }
        .sidebar-footer      {
          padding: 12px 8px;
          border-top: 1px solid var(--border);
          flex-shrink: 0;
        }
        .sidebar-version     { font-size: 0.7rem; color: var(--text-muted); text-align: center; padding-top: 8px; }
      `}</style>
        </aside>
    )
}
