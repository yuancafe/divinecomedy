import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { EntityDetailDrawer } from '../components/entity-detail-drawer'
import { EntityDictionary } from '../components/entity-dictionary'
import { KnowledgeGraphExplorer } from '../components/knowledge-graph-explorer'
import type { SiteData } from '../data-loader'

export function GraphPage({ data }: { data: SiteData }) {
  const navigate = useNavigate()
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const entityMap = Object.fromEntries(data.entities.map((entity) => [entity.id, entity]))
  const graphImageMap = Object.fromEntries(
    [...data.graphFull.nodes, ...data.graphCore.nodes]
      .filter((node) => node.image)
      .map((node) => [node.id, node.image]),
  )
  const selectedEntity = selectedEntityId
    ? entityMap[selectedEntityId]
      ? {
          ...entityMap[selectedEntityId],
          illustration: graphImageMap[selectedEntityId] ?? entityMap[selectedEntityId].illustration,
        }
      : null
    : null

  function openEntity(entityId: string) {
    setSelectedEntityId(entityId)
    setDrawerOpen(true)
  }

  function jumpToCanto(cantoId: number) {
    const realm =
      cantoId <= 34 ? 'inferno' : cantoId <= 67 ? 'purgatorio' : 'paradiso'
    navigate(`/${realm}?canto=${cantoId}`)
  }

  return (
    <div className="stack-page">
      <section className="section-heading page-intro">
        <div>
          <p className="eyebrow">知识图谱</p>
          <h1>神曲知识图谱</h1>
        </div>
        <p>图谱说明：先看核心，再看全图。默认显示 49 个核心节点；单击聚焦，双击打开完整实体卡，再切换到完整图谱查看长尾关系。</p>
      </section>

      <KnowledgeGraphExplorer
        coreGraph={data.graphCore}
        entities={data.entities}
        fullGraph={data.graphFull}
        onOpenEntity={openEntity}
        onSelectEntity={setSelectedEntityId}
        selectedEntityId={selectedEntityId}
      />

      <EntityDictionary coreGraph={data.graphCore} entities={data.entities} onOpenEntity={openEntity} />

      <EntityDetailDrawer
        entity={selectedEntity}
        entityMap={entityMap}
        onClose={() => {
          setDrawerOpen(false)
          setSelectedEntityId(null)
        }}
        onJumpToCanto={jumpToCanto}
        onSelectEntity={openEntity}
        open={drawerOpen}
      />
    </div>
  )
}
