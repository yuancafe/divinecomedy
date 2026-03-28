import { useDeferredValue, useMemo, useState } from 'react'

import { getCategoryLabel } from '../lib/utils'
import type { EntityCategory, EntityRecord, GraphData } from '../types'

const dictionaryCategories: Array<'all' | EntityCategory> = [
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

const categoryRank: Record<EntityCategory, number> = {
  Person: 0,
  Place: 1,
  Event: 2,
  Concept: 3,
  Document: 4,
  Organization: 5,
  Period: 6,
  Artifact: 7,
  Other: 8,
}

export function EntityDictionary({
  entities,
  coreGraph,
  onOpenEntity,
}: {
  entities: EntityRecord[]
  coreGraph: GraphData
  onOpenEntity: (entityId: string) => void
}) {
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState<'all' | EntityCategory>('all')
  const deferredQuery = useDeferredValue(query.trim().toLowerCase())
  const coreIds = useMemo(() => new Set(coreGraph.nodes.map((node) => node.id)), [coreGraph.nodes])

  const visibleEntities = useMemo(() => {
    return entities
      .filter((entity) => {
        const categoryPass = category === 'all' || entity.category === category
        const queryPass = !deferredQuery || entity.searchIndex.includes(deferredQuery)
        return categoryPass && queryPass
      })
      .sort((left, right) => {
        const leftCore = coreIds.has(left.id) ? 0 : 1
        const rightCore = coreIds.has(right.id) ? 0 : 1
        if (leftCore !== rightCore) return leftCore - rightCore
        const categoryDelta = categoryRank[left.category] - categoryRank[right.category]
        if (categoryDelta !== 0) return categoryDelta
        if (left.degree !== right.degree) return right.degree - left.degree
        if (left.occurrences.length !== right.occurrences.length) {
          return right.occurrences.length - left.occurrences.length
        }
        return left.nameZh.localeCompare(right.nameZh, 'zh-Hans-CN')
      })
      .slice(0, 240)
  }, [category, coreIds, deferredQuery, entities])

  return (
    <section className="dictionary-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">实体词典</p>
          <h2>实体词典</h2>
        </div>
        <label className="search-field">
          <span>检索</span>
          <input
            onChange={(event) => setQuery(event.target.value)}
            placeholder="搜索中文名、英文名或别名"
            value={query}
          />
        </label>
      </div>

      <div className="category-strip">
        {dictionaryCategories.map((item) => (
          <button
            key={item}
            className={category === item ? 'filter-chip active' : 'filter-chip'}
            onClick={() => setCategory(item)}
            type="button"
          >
            {item === 'all' ? '全部' : getCategoryLabel(item)}
          </button>
        ))}
      </div>

      <div className="dictionary-grid">
        {visibleEntities.map((entity) => (
          <button className="dictionary-card" key={entity.id} onClick={() => onOpenEntity(entity.id)} type="button">
            <div className="dictionary-card-head">
              <strong>{entity.nameZh}</strong>
              <span className="dictionary-card-category">{getCategoryLabel(entity.category)}</span>
            </div>
            <p className="dictionary-card-foreign">
              {entity.nameIt === entity.nameEn ? entity.nameEn : `${entity.nameIt} / ${entity.nameEn}`}
            </p>
            <small className="dictionary-card-occurrences">
              {entity.occurrences.slice(0, 3).map((occurrence) => occurrence.label).join(' · ') || '暂无篇歌索引'}
            </small>
          </button>
        ))}
      </div>
    </section>
  )
}
