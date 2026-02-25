import { renderHook, act } from '@testing-library/react'
import '@testing-library/jest-dom'
import { useApi } from '../../hooks/useApi'

describe('useApi', () => {
    it('initialises with null data and false loading', () => {
        const { result } = renderHook(() => useApi(jest.fn()))
        expect(result.current.data).toBeNull()
        expect(result.current.loading).toBe(false)
        expect(result.current.error).toBeNull()
    })

    it('sets loading=true during fetch and resolves data', async () => {
        const mockFn = jest.fn().mockResolvedValue({ foo: 'bar' })
        const { result } = renderHook(() => useApi(mockFn))

        await act(async () => { await result.current.execute() })

        expect(result.current.loading).toBe(false)
        expect(result.current.data).toEqual({ foo: 'bar' })
        expect(result.current.error).toBeNull()
    })

    it('sets error when the API call rejects', async () => {
        const mockFn = jest.fn().mockRejectedValue(new Error('Network error'))
        const { result } = renderHook(() => useApi(mockFn))

        await act(async () => { await result.current.execute() })

        expect(result.current.loading).toBe(false)
        expect(result.current.data).toBeNull()
        expect(result.current.error).toBe('Network error')
    })

    it('reset clears state', async () => {
        const mockFn = jest.fn().mockResolvedValue({ value: 42 })
        const { result } = renderHook(() => useApi(mockFn))

        await act(async () => { await result.current.execute() })
        expect(result.current.data).toEqual({ value: 42 })

        act(() => { result.current.reset() })
        expect(result.current.data).toBeNull()
        expect(result.current.error).toBeNull()
    })

    it('passes arguments to the API function', async () => {
        const mockFn = jest.fn().mockResolvedValue({})
        const { result } = renderHook(() => useApi(mockFn))

        await act(async () => { await result.current.execute('arg1', 42, { flag: true }) })

        expect(mockFn).toHaveBeenCalledWith('arg1', 42, { flag: true })
    })
})
