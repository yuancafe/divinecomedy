export type Realm = 'inferno' | 'purgatorio' | 'paradiso'

export type GraphMode = 'core' | 'full'

export type EntityCategory =
  | 'Person'
  | 'Place'
  | 'Event'
  | 'Concept'
  | 'Document'
  | 'Organization'
  | 'Period'
  | 'Artifact'
  | 'Other'

export interface WorkMeta {
  id: string
  title: string
  displayTitle: string
  translator: string
  language: string
  source: string
  kind: string
  format: string
}

export type ReaderPanelKind = 'text' | 'notes'

export interface ReaderNoteEntry {
  number: number
  content: string
}

export interface ReaderPanel {
  id: string
  workId: string
  kind: ReaderPanelKind
  label: string
  content: string
  contentHtml?: string
  noteEntries?: ReaderNoteEntry[]
}

export interface ReaderCanto {
  id: number
  realm: Realm
  realmLabel: string
  cantoNumber: number
  globalNumber: number
  title: string
  summary: string
  panels: ReaderPanel[]
}

export interface CantoOccurrence {
  cantoId: number
  realm: Realm
  cantoNumber: number
  label: string
}

export interface IllustrationAsset {
  id: string
  src: string
  title: string
  credit: string
  source: string
  usage: string[]
  width?: number
  height?: number
}

export interface EntityRecord {
  id: string
  entityKey: string
  nameZh: string
  nameIt: string
  nameEn: string
  category: EntityCategory
  description: string
  summary: string
  degree: number
  aliases: string[]
  occurrences: CantoOccurrence[]
  relatedEntities: string[]
  illustration?: IllustrationAsset | null
  searchIndex: string
}

export interface EntityMentionRecord {
  entityId: string
  cantoId: number
  realm: Realm
  cantoNumber: number
  label: string
}

export interface GraphNode {
  id: string
  label: string
  name: string
  category: EntityCategory
  degree: number
  image?: IllustrationAsset | null
}

export interface GraphEdge {
  id: string
  source: string
  target: string
}

export interface GraphData {
  nodes: GraphNode[]
  links: GraphEdge[]
}

export interface SceneLayer {
  id: 'medieval' | 'structure'
  label?: string
  image: IllustrationAsset
}

export interface RegionShape {
  id: string
  name: string
  type: 'region'
  cantoRange: [number, number]
  box: {
    x: number
    y: number
    w: number
    h: number
  }
  summary: string
}

export interface SceneHotspot {
  id: string
  kind: 'entity' | 'event'
  entityId: string
  label: string
  x: number
  y: number
  summary: string
  cantoIds: number[]
}

export interface OverviewPanel {
  realm: Realm
  title: string
  subtitle: string
  href: string
  layers: SceneLayer[]
  cantoGrid: {
    cantoId: number
    label: string
  }[]
}

export interface OverviewScene {
  id: string
  title: string
  layers: SceneLayer[]
  panels: OverviewPanel[]
}

export interface RealmScene {
  id: Realm
  realm: Realm
  title: string
  englishTitle: string
  layers: SceneLayer[]
  regions: RegionShape[]
  hotspots: SceneHotspot[]
  defaultCantoId: number
}

export interface MapScenesData {
  overview: OverviewScene
  realms: Record<Realm, RealmScene>
}

export interface ManifestData {
  counts: Record<string, number>
  hero: {
    title: string
    subtitle: string
    quote: string
  }
  defaultReaderColumns: string[]
  defaultReaderColumnCount: 1 | 2 | 3 | 4
}

export interface DantePageData {
  hero: ManifestData['hero']
  timeline: {
    year: string
    title: string
    body: string
  }[]
  illustrations: IllustrationAsset[]
  sections: {
    title: string
    body: string
  }[]
}

export interface AboutPageData {
  sections: {
    title: string
    body: string
  }[]
  illustrations: IllustrationAsset[]
}

export interface EpicComparisonRow {
  [key: string]: string
}
