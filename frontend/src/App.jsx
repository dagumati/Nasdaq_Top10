import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout/Layout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import GlobalScreener from './pages/GlobalScreener.jsx'
import WeeklyRecommendations from './pages/WeeklyRecommendations.jsx'
import ModelPortfolios from './pages/ModelPortfolios.jsx'
import DCASimulator from './pages/DCASimulator.jsx'
import NasdaqRotation from './pages/NasdaqRotation.jsx'

export default function App() {
    return (
        <Layout>
            <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/screener" element={<GlobalScreener />} />
                <Route path="/recommendations" element={<WeeklyRecommendations />} />
                <Route path="/portfolios" element={<ModelPortfolios />} />
                <Route path="/dca" element={<DCASimulator />} />
                <Route path="/nasdaq" element={<NasdaqRotation />} />
            </Routes>
        </Layout>
    )
}
