import React from 'react'
import { Sun, Moon, Wifi, WifiOff } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext.jsx'
import { useLocation } from 'react-router-dom'

const PAGE_TITLES = {
    '/': '🏠 Dashboard',
    '/screener': '🌍 Global Market Screener',
    '/recommendations': '💰 Weekly Investment Picks',
    '/portfolios': '🏗️ Model Portfolios',
    '/dca': '📈 DCA Simulator',
    '/nasdaq': '📊 Nasdaq Rotation',
}

export default function Navbar({ apiOnline }) {
    const { theme, toggle } = useTheme()
    const { pathname } = useLocation()
    const title = PAGE_TITLES[pathname] || '🌍 Global Investor'

    return (
        <header className="navbar">
            <div className="navbar-title">{title}</div>

            <div className="navbar-actions">
                {/* API status */}
                <div className={`api-status ${apiOnline ? 'online' : 'offline'}`}>
                    {apiOnline ? <Wifi size={14} /> : <WifiOff size={14} />}
                    <span>API {apiOnline ? 'Online' : 'Offline'}</span>
                </div>

                {/* Theme toggle */}
                <button
                    className="theme-toggle"
                    onClick={toggle}
                    aria-label="Toggle theme"
                    title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
                >
                    {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
                </button>
            </div>

            <style>{`
        .navbar {
          position: fixed;
          top: 0;
          left: var(--sidebar-w);
          right: 0;
          height: var(--navbar-h);
          background: var(--bg-secondary);
          border-bottom: 1px solid var(--border);
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 24px;
          z-index: 99;
          backdrop-filter: blur(8px);
        }
        .navbar-title {
          font-size: 1.05rem;
          font-weight: 600;
          color: var(--text-primary);
        }
        .navbar-actions { display: flex; align-items: center; gap: 12px; }
        .api-status {
          display: flex; align-items: center; gap: 6px;
          font-size: 0.78rem; font-weight: 500;
          padding: 5px 10px;
          border-radius: 99px;
          border: 1px solid;
        }
        .api-status.online  { color: var(--success); border-color: rgba(0,212,170,0.3); background: rgba(0,212,170,0.08); }
        .api-status.offline { color: var(--danger);  border-color: rgba(255,107,107,0.3); background: rgba(255,107,107,0.08); }
        .theme-toggle {
          width: 38px; height: 38px;
          border-radius: var(--radius-sm);
          border: 1px solid var(--border);
          background: var(--bg-card);
          color: var(--text-secondary);
          display: flex; align-items: center; justify-content: center;
          cursor: pointer;
          transition: all var(--transition);
        }
        .theme-toggle:hover { border-color: var(--accent); color: var(--accent); background: var(--bg-card-hover); }
      `}</style>
        </header>
    )
}
