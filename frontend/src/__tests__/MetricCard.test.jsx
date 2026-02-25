import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import MetricCard from '../../components/Cards/MetricCard'

describe('MetricCard', () => {
    it('renders label and value', () => {
        render(<MetricCard label="Total Assets" value="150+" />)
        expect(screen.getByText('Total Assets')).toBeInTheDocument()
        expect(screen.getByText('150+')).toBeInTheDocument()
    })

    it('renders delta when provided', () => {
        render(<MetricCard label="CAGR" value="12%" delta="+2% vs benchmark" deltaType="positive" />)
        expect(screen.getByText('+2% vs benchmark')).toBeInTheDocument()
    })

    it('does not render delta when not provided', () => {
        const { container } = render(<MetricCard label="CAGR" value="12%" />)
        expect(container.querySelector('.metric-delta')).toBeNull()
    })
})
