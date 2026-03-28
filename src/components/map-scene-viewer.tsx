import type { CSSProperties } from 'react'

import { ArtworkImage } from './artwork-image'
import { cn } from '../lib/utils'
import type { RealmScene } from '../types'

export function MapSceneViewer({
  scene,
  selectedLayer,
  selectedRegionId,
  selectedEntityId,
  onSelectLayer,
  onSelectRegion,
  onSelectHotspot,
}: {
  scene: RealmScene
  selectedLayer: 'medieval' | 'structure'
  selectedRegionId?: string
  selectedEntityId?: string | null
  onSelectLayer: (layer: 'medieval' | 'structure') => void
  onSelectRegion: (regionId: string) => void
  onSelectHotspot: (entityId: string) => void
}) {
  const layer = scene.layers.find((item) => item.id === selectedLayer) ?? scene.layers[0]
  const fallbackLayer = scene.layers.find((item) => item.id !== layer.id) ?? scene.layers[0]
  const canvasStyle: CSSProperties | undefined =
    layer.image.width && layer.image.height
      ? ({
          aspectRatio: `${layer.image.width} / ${layer.image.height}`,
          ['--scene-ratio' as string]: String(layer.image.width / layer.image.height),
        } as CSSProperties)
      : undefined

  return (
    <section className={`map-scene-card map-scene-card-${scene.realm}`} data-layer={selectedLayer}>
      <div className="map-scene-toolbar">
        <div>
          <p className="eyebrow">二维地图</p>
          <h1>{scene.title}地图</h1>
        </div>
        <div className="layer-toggle" role="tablist" aria-label="切换地图图层">
          {scene.layers.map((item) => (
            <button
              key={item.id}
              className={selectedLayer === item.id ? 'toggle-active' : ''}
              onClick={() => onSelectLayer(item.id)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      <div className="map-scene-stage">
        <div className="map-scene-canvas" style={canvasStyle}>
          <ArtworkImage
            alt={layer.image.title}
            className="map-scene-image"
            fallbackSrc={fallbackLayer.image.src}
            src={layer.image.src}
          />
          <div className="map-scene-overlay">
            {scene.regions.map((region) => (
              <button
                key={region.id}
                className={cn('map-region', selectedRegionId === region.id && 'map-region-active')}
                onClick={() => onSelectRegion(region.id)}
                style={{
                  left: `${region.box.x}%`,
                  top: `${region.box.y}%`,
                  width: `${region.box.w}%`,
                  height: `${region.box.h}%`,
                }}
                type="button"
              >
                <span>{region.name}</span>
              </button>
            ))}

            {scene.hotspots.map((hotspot) => (
              <button
                key={hotspot.id}
                className={cn('map-hotspot', selectedEntityId === hotspot.entityId && 'map-hotspot-active')}
                onClick={() => onSelectHotspot(hotspot.entityId)}
                style={{ left: `${hotspot.x}%`, top: `${hotspot.y}%` }}
                title={hotspot.summary}
                type="button"
              >
                <span className="map-hotspot-dot" />
                <span className="map-hotspot-label">{hotspot.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
