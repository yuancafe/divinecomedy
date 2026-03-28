import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { CantoSidebar } from '../components/canto-sidebar'
import { EntityDetailDrawer } from '../components/entity-detail-drawer'
import { MapSceneViewer } from '../components/map-scene-viewer'
import { TextComparisonDrawer } from '../components/text-comparison-drawer'
import type { SiteData } from '../data-loader'
import {
  buildDefaultReaderColumns,
  clampReaderColumnCount,
  createDefaultReaderColumnWidths,
  normalizeReaderColumnWidths,
} from '../lib/site-data'
import { buildWorkLookup } from '../lib/utils'
import type { Realm } from '../types'

type DrawerMode = 'reader' | 'entity'

export function RealmPage({
  data,
  realm,
}: {
  data: SiteData
  realm: Realm
}) {
  const [searchParams] = useSearchParams()
  const realmCantos = useMemo(
    () => data.readerCantos.filter((canto) => canto.realm === realm),
    [data.readerCantos, realm],
  )
  const scene = data.mapScenes.realms[realm]
  const cantoQuery = searchParams.get('canto')
  const hasCantoQuery = searchParams.has('canto')
  const queryInitial = Number(cantoQuery ?? scene.defaultCantoId)
  const initialCantoId = realmCantos.some((canto) => canto.id === queryInitial)
    ? queryInitial
    : scene.defaultCantoId
  const [selectedCantoId, setSelectedCantoId] = useState(initialCantoId)
  const [selectedLayer, setSelectedLayer] = useState<'medieval' | 'structure'>('medieval')
  const [drawerMode, setDrawerMode] = useState<DrawerMode>('reader')
  const [panelVisible, setPanelVisible] = useState(hasCantoQuery)
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null)
  const [readerColumns, setReaderColumns] = useState(data.manifest.defaultReaderColumns)
  const [readerColumnCount, setReaderColumnCount] = useState(data.manifest.defaultReaderColumnCount)
  const [readerColumnWidths, setReaderColumnWidths] = useState(createDefaultReaderColumnWidths())

  const worksById = useMemo(() => buildWorkLookup(data.works), [data.works])
  const selectedCanto =
    data.readerCantos.find((canto) => canto.id === selectedCantoId) ?? realmCantos[0]
  const availablePanelIds = useMemo(
    () => new Set(selectedCanto.panels.map((panel) => panel.id)),
    [selectedCanto.panels],
  )
  const defaultPanels = useMemo(
    () =>
      buildDefaultReaderColumns(
        selectedCanto.panels.map((panel) => ({
          id: panel.id,
          workId: panel.workId,
          language: worksById[panel.workId]?.language ?? 'zh',
          kind: panel.kind,
        })),
      ),
    [selectedCanto.panels, worksById],
  )
  const selectedRegion = scene.regions.find(
    (region) =>
      selectedCanto.cantoNumber >= region.cantoRange[0] &&
      selectedCanto.cantoNumber <= region.cantoRange[1],
  )
  const entityMap = Object.fromEntries(data.entities.map((entity) => [entity.id, entity]))
  const selectedEntity = selectedEntityId ? entityMap[selectedEntityId] ?? null : null

  const resolvedReaderColumns = useMemo(() => {
    const fallback = defaultPanels[0] ?? selectedCanto.panels[0]?.id ?? ''
    return Array.from({ length: 4 }, (_, index) => {
      const existing = readerColumns[index]
      if (existing && availablePanelIds.has(existing)) {
        return existing
      }
      return defaultPanels[index] ?? fallback
    }).filter(Boolean)
  }, [availablePanelIds, defaultPanels, readerColumns, selectedCanto.panels])

  function openReaderForCanto(cantoId: number) {
    setSelectedCantoId(cantoId)
    setSelectedEntityId(null)
    setDrawerMode('reader')
    setPanelVisible(true)
  }

  function openEntity(entityId: string) {
    const entity = entityMap[entityId]
    if (!entity) return
    setSelectedEntityId(entityId)
    if (entity.occurrences[0]) {
      setSelectedCantoId(entity.occurrences[0].cantoId)
    }
    setDrawerMode('entity')
    setPanelVisible(true)
  }

  return (
    <div className="world-layout">
      <CantoSidebar
        cantos={realmCantos}
        onSelect={openReaderForCanto}
        selectedCantoId={selectedCanto.id}
        title={scene.title}
      />

      <section className="world-main">
        <MapSceneViewer
          onSelectHotspot={openEntity}
          onSelectLayer={setSelectedLayer}
          onSelectRegion={(regionId) => {
            const region = scene.regions.find((item) => item.id === regionId)
            if (!region) return
            const target = realmCantos.find(
              (canto) =>
                canto.cantoNumber >= region.cantoRange[0] &&
                canto.cantoNumber <= region.cantoRange[1],
            )
            if (target) openReaderForCanto(target.id)
          }}
          scene={scene}
          selectedEntityId={selectedEntityId}
          selectedLayer={selectedLayer}
          selectedRegionId={selectedRegion?.id}
        />
        {!panelVisible ? (
          <button
            className="panel-peek-button"
            onClick={() => setPanelVisible(true)}
            type="button"
          >
            打开右侧面板
          </button>
        ) : null}
      </section>

      <TextComparisonDrawer
        canto={selectedCanto}
        columnCount={readerColumnCount}
        columns={resolvedReaderColumns}
        onChangeColumn={(index, panelId) =>
          setReaderColumns((current) =>
            Array.from({ length: 4 }, (_, itemIndex) =>
              itemIndex === index
                ? panelId
                : resolvedReaderColumns[itemIndex] ?? current[itemIndex] ?? panelId,
            ),
          )
        }
        onChangeColumnCount={(count) => {
          const nextCount = clampReaderColumnCount(count)
          setReaderColumnCount(nextCount)
          setReaderColumnWidths((current) => normalizeReaderColumnWidths(current, nextCount))
        }}
        onChangeColumnWidths={(widths) => setReaderColumnWidths(widths)}
        onClose={() => setPanelVisible(false)}
        open={panelVisible && drawerMode === 'reader'}
        widths={normalizeReaderColumnWidths(readerColumnWidths, readerColumnCount)}
        works={data.works}
      />

      <EntityDetailDrawer
        entity={selectedEntity}
        entityMap={entityMap}
        onClose={() => {
          setPanelVisible(false)
          setSelectedEntityId(null)
        }}
        onJumpToCanto={openReaderForCanto}
        onSelectEntity={openEntity}
        open={panelVisible && drawerMode === 'entity'}
      />
    </div>
  )
}
