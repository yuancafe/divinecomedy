import { useDeferredValue, useEffect, useEffectEvent, useMemo, useRef, useState } from 'react'
import { Network } from 'vis-network/standalone'

import { getCategoryLabel } from '../lib/utils'
import type { EntityCategory, EntityRecord, GraphData, GraphMode } from '../types'

const categoryOrder: Array<'all' | EntityCategory> = [
  'all',
  'Person',
  'Place',
  'Event',
  'Concept',
  'Document',
  'Organization',
  'Period',
  'Artifact',
  'Other',
]

const colorMap: Record<EntityCategory, string> = {
  Person: '#d2a35d',
  Place: '#89a9c9',
  Event: '#b96a4b',
  Concept: '#8577b4',
  Document: '#c3a98e',
  Organization: '#73906f',
  Period: '#7db2a3',
  Artifact: '#c67695',
  Other: '#8c949a',
}

export function KnowledgeGraphExplorer({
  coreGraph,
  fullGraph,
  entities,
  selectedEntityId,
  onSelectEntity,
  onOpenEntity,
}: {
  coreGraph: GraphData
  fullGraph: GraphData
  entities: EntityRecord[]
  selectedEntityId: string | null
  onSelectEntity: (entityId: string) => void
  onOpenEntity: (entityId: string) => void
}) {
  const entityMap = useMemo(
    () => Object.fromEntries(entities.map((entity) => [entity.id, entity])),
    [entities],
  )
  const containerRef = useRef<HTMLDivElement | null>(null)
  const networkRef = useRef<Network | null>(null)
  const [mode, setMode] = useState<GraphMode>('core')
  const [visibleCategory, setVisibleCategory] = useState<'all' | EntityCategory>('all')
  const [query, setQuery] = useState('')
  const deferredQuery = useDeferredValue(query.trim().toLowerCase())
  const graph = mode === 'core' ? coreGraph : fullGraph

  const nodes = useMemo(() => {
    return graph.nodes.filter((node) => {
      const categoryPass = visibleCategory === 'all' || node.category === visibleCategory
      if (!categoryPass) return false
      if (!deferredQuery) return true
      const entity = entityMap[node.id]
      return (entity?.searchIndex ?? node.label.toLowerCase()).includes(deferredQuery)
    })
  }, [deferredQuery, entityMap, graph.nodes, visibleCategory])

  const nodeIds = useMemo(() => new Set(nodes.map((node) => node.id)), [nodes])
  const edges = useMemo(
    () => graph.links.filter((link) => nodeIds.has(link.source) && nodeIds.has(link.target)),
    [graph.links, nodeIds],
  )

  const handleSelectNode = useEffectEvent((nodeId: string) => {
    onSelectEntity(nodeId)
  })

  useEffect(() => {
    if (!containerRef.current) return

    const showAllLabels = mode === 'core'

    const visNodes = nodes.map((node) => ({
      id: node.id,
      label: showAllLabels || node.degree >= 7 || node.id === selectedEntityId ? node.label : '',
      value: Math.max(node.degree * 2.2, 12),
      image: node.image?.src,
      shape: node.image?.src ? 'image' : 'dot',
      size: Math.max(node.degree * (showAllLabels ? 2.8 : 2.3), showAllLabels ? 26 : 18),
      title: `${node.label} · ${getCategoryLabel(node.category)}`,
      color: {
        background: colorMap[node.category],
        border: '#e8ddbf',
        highlight: {
          background: '#f3d485',
          border: '#f8ebc3',
        },
      },
      font: {
        color: '#2b2115',
        face: 'Baskerville',
        size: showAllLabels ? 18 : 15,
        strokeColor: 'rgba(251, 245, 230, 0.92)',
        strokeWidth: 6,
        vadjust: showAllLabels ? 42 : 26,
      },
      borderWidth: node.id === selectedEntityId ? 4 : 2.6,
      shadow: {
        enabled: true,
        color: 'rgba(37, 25, 14, 0.24)',
        size: 16,
        x: 0,
        y: 6,
      },
    }))

    const visEdges = edges.map((edge) => ({
      id: edge.id,
      from: edge.source,
      to: edge.target,
      color: {
        color: 'rgba(194, 172, 126, 0.16)',
        highlight: '#d7bb71',
      },
      width: 0.9,
    }))

    if (!networkRef.current) {
      networkRef.current = new Network(
        containerRef.current,
        {
          nodes: visNodes,
          edges: visEdges,
        },
        {
          autoResize: true,
          interaction: {
            hover: true,
            tooltipDelay: 80,
            navigationButtons: false,
          },
          physics: {
            stabilization: {
              iterations: 120,
            },
            barnesHut: {
              gravitationalConstant: -12000,
              centralGravity: 0.12,
              springLength: 120,
              springConstant: 0.035,
            },
          },
          nodes: {
            shape: 'dot',
            borderWidth: 2.8,
            shapeProperties: {
              useBorderWithImage: true,
            },
            scaling: {
              min: 20,
              max: 62,
            },
          },
          edges: {
            smooth: {
              enabled: true,
              type: 'continuous',
              roundness: 0.5,
            },
          },
        },
      )

      networkRef.current.on('selectNode', (params: { nodes: string[] }) => {
        if (params.nodes.length > 0) {
          handleSelectNode(params.nodes[0])
        }
      })

      networkRef.current.on('doubleClick', (params: { nodes: string[] }) => {
        if (params.nodes.length > 0) {
          onOpenEntity(params.nodes[0])
        }
      })
    } else {
      networkRef.current.setData({
        nodes: visNodes,
        edges: visEdges,
      })
    }

    if (selectedEntityId && nodeIds.has(selectedEntityId)) {
      networkRef.current.selectNodes([selectedEntityId])
      networkRef.current.focus(selectedEntityId, {
        scale: 1.12,
        animation: {
          duration: 500,
          easingFunction: 'easeInOutQuad',
        },
      })
    } else {
      networkRef.current.fit({
        animation: {
          duration: 500,
          easingFunction: 'easeInOutQuad',
        },
      })
    }
  }, [edges, mode, nodeIds, nodes, onOpenEntity, selectedEntityId])

  useEffect(() => {
    return () => {
      networkRef.current?.destroy()
      networkRef.current = null
    }
  }, [])

  return (
    <section className="graph-explorer">
      <div className="graph-toolbar">
        <div className="graph-modes">
          <button
            className={mode === 'core' ? 'segmented-button active' : 'segmented-button'}
            onClick={() => setMode('core')}
            type="button"
          >
            核心图谱
          </button>
          <button
            className={mode === 'full' ? 'segmented-button active' : 'segmented-button'}
            onClick={() => setMode('full')}
            type="button"
          >
            完整图谱
          </button>
        </div>
        <label className="search-field">
          <span>搜索实体</span>
          <input
            onChange={(event) => setQuery(event.target.value)}
            placeholder="输入 维吉尔 / 弗兰切斯卡 / 炼狱之门"
            value={query}
          />
        </label>
      </div>

      <div className="category-strip">
        {categoryOrder.map((category) => (
          <button
            key={category}
            className={visibleCategory === category ? 'filter-chip active' : 'filter-chip'}
            onClick={() => setVisibleCategory(category)}
            type="button"
          >
            {category === 'all' ? '全部' : getCategoryLabel(category)}
          </button>
        ))}
      </div>

      <div className="graph-canvas-card graph-canvas-card-full">
        <div className="graph-canvas-meta">
          <p>当前显示 {nodes.length} 个节点，单击聚焦，双击打开完整实体卡。</p>
          <button
            className="ghost-button"
            onClick={() =>
              networkRef.current?.fit({
                animation: {
                  duration: 500,
                  easingFunction: 'easeInOutQuad',
                },
              })
            }
            type="button"
          >
            重新铺满
          </button>
        </div>
        <div className="graph-canvas" ref={containerRef} />
      </div>
    </section>
  )
}
