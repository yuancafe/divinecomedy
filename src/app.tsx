import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { ErrorScreen } from './components/error-screen'
import { LoadingScreen } from './components/loading-screen'
import { SiteShell } from './components/site-shell'
import { useSiteData } from './hooks/use-site-data'
import { AboutPage } from './pages/about-page'
import { DantePage } from './pages/dante-page'
import { EpicStatusPage } from './pages/epic-status-page'
import { GraphPage } from './pages/graph-page'
import { HomePage } from './pages/home-page'
import { MapPage } from './pages/map-page'
import { RealmPage } from './pages/realm-page'

export default function App() {
  const { data, error, loading } = useSiteData()

  if (loading) return <LoadingScreen message="手抄本正在展开" />
  if (error || !data) return <ErrorScreen message={error ?? 'unknown error'} />

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<SiteShell />}>
          <Route element={<HomePage data={data} />} path="/" />
          <Route element={<DantePage data={data} />} path="/dante" />
          <Route element={<AboutPage data={data} />} path="/about" />
          <Route element={<MapPage data={data} />} path="/map" />
          <Route element={<RealmPage data={data} key="inferno" realm="inferno" />} path="/inferno" />
          <Route element={<RealmPage data={data} key="purgatorio" realm="purgatorio" />} path="/purgatorio" />
          <Route element={<RealmPage data={data} key="paradiso" realm="paradiso" />} path="/paradiso" />
          <Route element={<GraphPage data={data} />} path="/graph" />
          <Route element={<EpicStatusPage data={data} />} path="/epic-status" />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
