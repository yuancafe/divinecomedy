import { ArtworkImage } from './artwork-image'
import { getCategoryLabel } from '../lib/utils'
import type { EntityRecord } from '../types'

export function EntityDetailDrawer({
  entity,
  open,
  onClose,
  onJumpToCanto,
  onSelectEntity,
  entityMap,
}: {
  entity: EntityRecord | null
  open: boolean
  onClose: () => void
  onJumpToCanto: (cantoId: number) => void
  onSelectEntity: (entityId: string) => void
  entityMap: Record<string, EntityRecord>
}) {
  return (
    <aside className={open ? 'reader-drawer reader-drawer-open entity-drawer' : 'reader-drawer entity-drawer'}>
      <div className="reader-drawer-header">
        <div>
          <p className="eyebrow">实体卡片</p>
          <h2>{entity?.nameZh ?? '实体详情'}</h2>
          <p>{entity?.summary ?? '点击人物、地点、事件或图谱节点后，在这里查看说明。'}</p>
        </div>
        <button
          className="drawer-close"
          onClick={(event) => {
            event.stopPropagation()
            onClose()
          }}
          type="button"
        >
          关闭
        </button>
      </div>

      {entity ? (
        <div className="entity-drawer-body">
          {entity.illustration ? (
            <figure className="entity-figure">
              <ArtworkImage alt={entity.illustration.title} src={entity.illustration.src} />
            </figure>
          ) : null}

          <div className="entity-meta-row">
            <span className="pill pill-solid">{getCategoryLabel(entity.category)}</span>
            <span className="pill">关联度 {entity.degree}</span>
            <span className="pill">{entity.occurrences.length} 处篇歌索引</span>
          </div>

          <dl className="entity-fields">
            <div>
              <dt>中文名</dt>
              <dd>{entity.nameZh}</dd>
            </div>
            <div>
              <dt>Italiano</dt>
              <dd>{entity.nameIt}</dd>
            </div>
            <div>
              <dt>English</dt>
              <dd>{entity.nameEn}</dd>
            </div>
            <div>
              <dt>别名</dt>
              <dd>{entity.aliases.slice(0, 6).join(' / ') || '—'}</dd>
            </div>
          </dl>

          <div className="entity-copy">
            <p>{entity.description}</p>
          </div>

          <section className="drawer-block">
            <div className="section-cap">出现篇歌</div>
            <div className="chip-row">
              {entity.occurrences.length > 0 ? (
                entity.occurrences.map((occurrence) => (
                  <button
                    key={`${entity.id}-${occurrence.cantoId}`}
                    className="chip-button"
                    onClick={() => onJumpToCanto(occurrence.cantoId)}
                    type="button"
                  >
                    {occurrence.label}
                  </button>
                ))
              ) : (
                <span className="empty-inline">当前未定位到可靠篇歌索引。</span>
              )}
            </div>
          </section>

          <section className="drawer-block">
            <div className="section-cap">相关实体</div>
            <div className="chip-row">
              {entity.relatedEntities
                .filter((relatedId) => entityMap[relatedId])
                .slice(0, 18)
                .map((relatedId) => (
                  <button
                    key={relatedId}
                    className="chip-button"
                    onClick={() => onSelectEntity(relatedId)}
                    type="button"
                  >
                    {entityMap[relatedId].nameZh}
                  </button>
                ))}
            </div>
          </section>
        </div>
      ) : null}
    </aside>
  )
}
