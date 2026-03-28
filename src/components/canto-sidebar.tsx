import { cn } from '../lib/utils'
import type { ReaderCanto } from '../types'

export function CantoSidebar({
  title,
  cantos,
  selectedCantoId,
  onSelect,
}: {
  title: string
  cantos: ReaderCanto[]
  selectedCantoId: number
  onSelect: (cantoId: number) => void
}) {
  return (
    <aside className="canto-sidebar">
      <div className="sidebar-header">
        <p className="eyebrow">目录</p>
        <h2>{title}</h2>
      </div>
      <div className="sidebar-scroll">
        {cantos.map((canto) => (
          <button
            key={canto.id}
            className={cn('sidebar-item', canto.id === selectedCantoId && 'sidebar-item-active')}
            onClick={() => onSelect(canto.id)}
            type="button"
          >
            <span className="sidebar-item-index">{String(canto.cantoNumber).padStart(2, '0')}</span>
            <span className="sidebar-item-copy">
              <strong>{canto.title}</strong>
            </span>
          </button>
        ))}
      </div>
    </aside>
  )
}
