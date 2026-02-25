import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { RatingBadge, ScoreBar, formatCurrency, formatPct } from '../../components/Cards/SharedUI'

describe('RatingBadge', () => {
    it.each([
        ['Strong Buy', 'badge-strong-buy'],
        ['Buy', 'badge-buy'],
        ['Hold', 'badge-hold'],
        ['Reduce', 'badge-reduce'],
        ['Avoid', 'badge-avoid'],
    ])('applies correct class for %s', (rating, cls) => {
        const { container } = render(<RatingBadge rating={rating} />)
        expect(container.firstChild).toHaveClass(cls)
        expect(screen.getByText(rating)).toBeInTheDocument()
    })
})

describe('ScoreBar', () => {
    it('renders a fill bar with correct width', () => {
        const { container } = render(<ScoreBar score={75} />)
        const fill = container.querySelector('.score-bar-fill')
        expect(fill.style.width).toBe('75%')
    })

    it('caps at 100%', () => {
        const { container } = render(<ScoreBar score={150} />)
        const fill = container.querySelector('.score-bar-fill')
        expect(fill.style.width).toBe('100%')
    })
})

describe('formatCurrency', () => {
    it('formats billions correctly', () => { expect(formatCurrency(2_500_000_000)).toBe('$2.5B') })
    it('formats millions correctly', () => { expect(formatCurrency(1_200_000)).toBe('$1.2M') })
    it('formats thousands correctly', () => { expect(formatCurrency(5_000)).toBe('$5.0K') })
    it('formats small amounts', () => { expect(formatCurrency(49.99)).toBe('$49.99') })
    it('returns dash for null', () => { expect(formatCurrency(null)).toBe('—') })
})

describe('formatPct', () => {
    it('adds + for positive', () => { expect(formatPct(12.5)).toBe('+12.5%') })
    it('no + for negative', () => { expect(formatPct(-3.2)).toBe('-3.2%') })
    it('returns dash for null', () => { expect(formatPct(null)).toBe('—') })
})
