import { useEffect, useState } from 'react'

import { loadSiteData, type SiteData } from '../data-loader'

export function useSiteData() {
  const [data, setData] = useState<SiteData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    loadSiteData()
      .then((value) => {
        if (!active) return
        setData(value)
        setLoading(false)
      })
      .catch((err: Error) => {
        if (!active) return
        setError(err.message)
        setLoading(false)
      })
    return () => {
      active = false
    }
  }, [])

  return { data, error, loading }
}
