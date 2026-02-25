import React, { useEffect, useState } from 'react'
import Sidebar from './Sidebar.jsx'
import Navbar from './Navbar.jsx'
import { healthApi } from '../../services/api.js'

export default function Layout({ children }) {
    const [apiOnline, setApiOnline] = useState(false)

    useEffect(() => {
        healthApi.check()
            .then(() => setApiOnline(true))
            .catch(() => setApiOnline(false))
    }, [])

    return (
        <div className="app-shell">
            <Sidebar />
            <Navbar apiOnline={apiOnline} />
            <main className="main-content">{children}</main>
        </div>
    )
}
