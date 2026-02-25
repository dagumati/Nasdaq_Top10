import { useState, useCallback } from 'react'

/**
 * Generic async data-fetching hook.
 * Usage:
 *   const { data, loading, error, execute } = useApi(screenerApi.run)
 *   execute('thematic', 15)
 */
export function useApi(apiFn) {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const execute = useCallback(async (...args) => {
        setLoading(true)
        setError(null)
        try {
            const result = await apiFn(...args)
            setData(result)
            return result
        } catch (err) {
            setError(err.message || 'Something went wrong')
            return null
        } finally {
            setLoading(false)
        }
    }, [apiFn])

    const reset = useCallback(() => {
        setData(null)
        setError(null)
        setLoading(false)
    }, [])

    return { data, loading, error, execute, reset }
}
