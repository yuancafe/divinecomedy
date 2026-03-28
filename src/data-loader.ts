import type {
  AboutPageData,
  DantePageData,
  EntityMentionRecord,
  EntityRecord,
  EpicComparisonRow,
  GraphData,
  IllustrationAsset,
  ManifestData,
  MapScenesData,
  ReaderCanto,
  WorkMeta,
} from './types'

export interface SiteData {
  manifest: ManifestData
  works: WorkMeta[]
  readerCantos: ReaderCanto[]
  entities: EntityRecord[]
  mentions: EntityMentionRecord[]
  mapScenes: MapScenesData
  illustrations: IllustrationAsset[]
  graphCore: GraphData
  graphFull: GraphData
  epicComparisons: EpicComparisonRow[]
  dantePage: DantePageData
  aboutPage: AboutPageData
}

let cache: Promise<SiteData> | null = null

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (!response.ok) {
    throw new Error(`Failed to load ${path}`)
  }
  return response.json() as Promise<T>
}

export function loadSiteData(): Promise<SiteData> {
  if (!cache) {
    cache = Promise.all([
      fetchJson<ManifestData>('/data/manifest.json'),
      fetchJson<WorkMeta[]>('/data/works.json'),
      fetchJson<ReaderCanto[]>('/data/reader-cantos.json'),
      fetchJson<EntityRecord[]>('/data/entity-catalog.json'),
      fetchJson<EntityMentionRecord[]>('/data/entity-mentions.json'),
      fetchJson<MapScenesData>('/data/map-scenes.json'),
      fetchJson<IllustrationAsset[]>('/data/illustrations.json'),
      fetchJson<GraphData>('/data/graph-core.json'),
      fetchJson<GraphData>('/data/graph-full.json'),
      fetchJson<EpicComparisonRow[]>('/data/epic-comparisons.json'),
      fetchJson<DantePageData>('/data/dante-page.json'),
      fetchJson<AboutPageData>('/data/about-page.json'),
    ]).then(
      ([
        manifest,
        works,
        readerCantos,
        entities,
        mentions,
        mapScenes,
        illustrations,
        graphCore,
        graphFull,
        epicComparisons,
        dantePage,
        aboutPage,
      ]) => ({
        manifest,
        works,
        readerCantos,
        entities,
        mentions,
        mapScenes,
        illustrations,
        graphCore,
        graphFull,
        epicComparisons,
        dantePage,
        aboutPage,
      }),
    )
  }
  return cache
}
