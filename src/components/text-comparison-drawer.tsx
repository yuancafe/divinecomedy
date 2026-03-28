import { useRef, useState } from 'react'

import { buildReaderColumnSlotKey } from '../lib/site-data'
import type { ReaderCanto, WorkMeta } from '../types'

const columnLabels = ['第一列', '第二列', '第三列', '第四列']

export function TextComparisonDrawer({
  canto,
  works,
  columns,
  columnCount,
  open,
  onClose,
  onChangeColumn,
  onChangeColumnCount,
  widths,
  onChangeColumnWidths,
}: {
  canto: ReaderCanto
  works: WorkMeta[]
  columns: string[]
  columnCount: 1 | 2 | 3 | 4
  open: boolean
  onClose: () => void
  onChangeColumn: (index: number, panelId: string) => void
  onChangeColumnCount: (count: 1 | 2 | 3 | 4) => void
  widths: number[]
  onChangeColumnWidths: (widths: number[]) => void
}) {
  const panelsRef = useRef<HTMLDivElement | null>(null)
  const panelBodyRefs = useRef<Array<HTMLDivElement | null>>([])
  const syncingScrollRef = useRef(false)
  const [syncScrollEnabled, setSyncScrollEnabled] = useState(false)
  const workLookup = Object.fromEntries(works.map((work) => [work.id, work]))
  const panelLookup = Object.fromEntries(canto.panels.map((panel) => [panel.id, panel]))
  const visibleColumns = columns.slice(0, columnCount)
  const visibleWidths = widths.slice(0, columnCount)

  function handleResizeStart(handleIndex: number, clientX: number) {
    const container = panelsRef.current
    if (!container) return
    const containerWidth = container.getBoundingClientRect().width
    if (!containerWidth) return
    const startX = clientX
    const startWidths = [...widths]

    function handleMove(event: PointerEvent) {
      const deltaPercent = ((event.clientX - startX) / containerWidth) * 100
      const nextWidths = [...startWidths]
      const minimum = columnCount >= 4 ? 12 : columnCount === 3 ? 16 : 18
      const left = nextWidths[handleIndex]
      const right = nextWidths[handleIndex + 1]
      const pair = left + right
      const nextLeft = Math.min(pair - minimum, Math.max(minimum, left + deltaPercent))
      nextWidths[handleIndex] = nextLeft
      nextWidths[handleIndex + 1] = pair - nextLeft
      onChangeColumnWidths(nextWidths)
    }

    function handleUp() {
      window.removeEventListener('pointermove', handleMove)
      window.removeEventListener('pointerup', handleUp)
    }

    window.addEventListener('pointermove', handleMove)
    window.addEventListener('pointerup', handleUp)
  }

  function handlePanelScroll(index: number) {
    if (!syncScrollEnabled || syncingScrollRef.current) return
    const source = panelBodyRefs.current[index]
    if (!source) return
    const scrollable = source.scrollHeight - source.clientHeight
    const ratio = scrollable > 0 ? source.scrollTop / scrollable : 0

    syncingScrollRef.current = true
    panelBodyRefs.current.slice(0, columnCount).forEach((panelBody, panelIndex) => {
      if (!panelBody || panelIndex === index) return
      const targetScrollable = panelBody.scrollHeight - panelBody.clientHeight
      panelBody.scrollTop = targetScrollable > 0 ? ratio * targetScrollable : 0
    })
    window.requestAnimationFrame(() => {
      syncingScrollRef.current = false
    })
  }

  return (
    <aside className={open ? 'reader-drawer reader-drawer-open' : 'reader-drawer'}>
      <div className="reader-drawer-header">
        <div>
          <p className="eyebrow">整歌对读</p>
          <h2>{canto.title}</h2>
        </div>
        <div className="reader-drawer-actions">
          <button
            aria-pressed={syncScrollEnabled}
            className={syncScrollEnabled ? 'drawer-toggle drawer-toggle-active' : 'drawer-toggle'}
            onClick={() => setSyncScrollEnabled((current) => !current)}
            type="button"
          >
            {syncScrollEnabled ? '同步滚动：开' : '同步滚动：关'}
          </button>
          <button className="drawer-close" onClick={onClose} type="button">
            收起正文
          </button>
        </div>
      </div>

      <div className="reader-column-controls">
        <div className="reader-column-count">
          <span>分栏</span>
          <div className="graph-modes reader-column-count-buttons">
            {[1, 2, 3, 4].map((count) => (
              <button
                key={count}
                className={columnCount === count ? 'segmented-button active' : 'segmented-button'}
                onClick={() => onChangeColumnCount(count as 1 | 2 | 3 | 4)}
                type="button"
              >
                {count} 栏
              </button>
            ))}
          </div>
        </div>

        {visibleColumns.map((value, index) => (
          <label className="reader-column-select" key={buildReaderColumnSlotKey(index, value)}>
            <span>{columnLabels[index]}</span>
            <select onChange={(event) => onChangeColumn(index, event.target.value)} value={value}>
              {canto.panels.map((panel) => {
                const work = workLookup[panel.workId]
                const suffix = panel.kind === 'notes' ? '注释' : '正文'
                return (
                  <option key={panel.id} value={panel.id}>
                    {work?.displayTitle ?? panel.label} · {suffix}
                  </option>
                )
              })}
            </select>
          </label>
        ))}
      </div>

      <div className="reader-panels" ref={panelsRef}>
        {visibleColumns.map((panelId, index) => {
          const panel = panelLookup[panelId]
          const work = panel ? workLookup[panel.workId] : null
          const slotKey = buildReaderColumnSlotKey(index, panelId)

          return (
            <div className="reader-panel-slot" key={slotKey} style={{ width: `${visibleWidths[index]}%` }}>
              <section className={panel?.kind === 'notes' ? 'reader-panel reader-panel-notes' : 'reader-panel'}>
                <header className="reader-panel-head">
                  <p>{columnLabels[index]}</p>
                  <strong>{work?.displayTitle ?? panel?.label ?? '未选择内容'}</strong>
                  <small>
                    {panel?.kind === 'notes'
                      ? `${work?.translator ?? '未知版本'} 注释`
                      : work?.translator ?? '未知版本'}
                  </small>
                </header>
                <div
                  className="reader-panel-body"
                  onScroll={() => handlePanelScroll(index)}
                  ref={(node) => {
                    panelBodyRefs.current[index] = node
                  }}
                >
                  <div className="reader-panel-content">
                    {panel?.contentHtml ? (
                      <div dangerouslySetInnerHTML={{ __html: panel.contentHtml }} />
                    ) : (
                      panel?.content?.trim() || (panel?.kind === 'notes' ? '本歌暂无可分离的注释内容。' : '本歌暂无正文。')
                    )}
                  </div>
                </div>
              </section>
              {index < visibleColumns.length - 1 ? (
                <button
                  aria-label={`调整${columnLabels[index]}与${columnLabels[index + 1]}宽度`}
                  className="reader-panel-resizer"
                  onPointerDown={(event) => {
                    event.preventDefault()
                    handleResizeStart(index, event.clientX)
                  }}
                  type="button"
                >
                  <span />
                </button>
              ) : null}
            </div>
          )
        })}
      </div>
    </aside>
  )
}
