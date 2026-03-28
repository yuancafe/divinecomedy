import { Link } from 'react-router-dom'

import { ArtworkImage } from './artwork-image'
import type { OverviewScene } from '../types'

export function OverviewTriptych({
  scene,
  selectedLayer,
  onSelectLayer,
}: {
  scene: OverviewScene
  selectedLayer: 'medieval' | 'structure'
  onSelectLayer: (layer: 'medieval' | 'structure') => void
}) {
  return (
    <section className="overview-triptych">
      <div className="section-heading triptych-heading">
        <div>
          <p className="eyebrow">神曲阅读</p>
          <h2>{scene.title}</h2>
        </div>
        <div className="layer-toggle" role="tablist" aria-label="切换总图图层">
          {scene.layers.map((layer) => (
            <button
              key={layer.id}
              className={selectedLayer === layer.id ? 'toggle-active' : ''}
              onClick={() => onSelectLayer(layer.id)}
              type="button"
            >
              {layer.label}
            </button>
          ))}
        </div>
      </div>
      <div className="triptych-grid">
        {scene.panels.map((panel) => {
          const layer = panel.layers.find((item) => item.id === selectedLayer) ?? panel.layers[0]
          const fallbackLayer = panel.layers.find((item) => item.id !== layer.id) ?? panel.layers[0]
          return (
            <article className="triptych-card" key={panel.realm}>
              <div className="triptych-frame">
                <ArtworkImage
                  alt={layer.image.title}
                  className="triptych-image"
                  fallbackSrc={fallbackLayer.image.src}
                  src={layer.image.src}
                />
                <div className="triptych-overlay">
                  <header className="triptych-meta">
                    <p className="triptych-subtitle">{panel.subtitle}</p>
                    <h3 className="triptych-title">{panel.title}</h3>
                  </header>
                  <div className="triptych-canto-grid">
                    {panel.cantoGrid.map((item) => (
                      <Link className="triptych-canto-link" key={item.cantoId} to={`${panel.href}?canto=${item.cantoId}`}>
                        {item.label}
                      </Link>
                    ))}
                  </div>
                </div>
              </div>
              <footer className="triptych-footer">
                <Link to={panel.href}>进入 {panel.subtitle}</Link>
              </footer>
            </article>
          )
        })}
      </div>
    </section>
  )
}
