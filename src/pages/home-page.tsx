import { useState } from 'react'
import { Link } from 'react-router-dom'

import { ArtworkImage } from '../components/artwork-image'
import { OverviewTriptych } from '../components/overview-triptych'
import type { SiteData } from '../data-loader'

export function HomePage({ data }: { data: SiteData }) {
  const [selectedLayer, setSelectedLayer] = useState<'medieval' | 'structure'>('medieval')
  const heroIllustration =
    data.illustrations.find((item) => item.id === 'home-hero-domenico') ?? data.mapScenes.overview.layers[0].image
  const heroMediaStyle =
    heroIllustration.width && heroIllustration.height
      ? { aspectRatio: `${heroIllustration.width} / ${heroIllustration.height}` }
      : undefined

  return (
    <div className="stack-page">
      <section className="home-hero-layout">
        <div className="home-hero-copy home-hero-copy-grid">
          <article className="info-card">
            <p className="eyebrow">Digital Dante Museum</p>
            <h1>但丁《神曲》数字阅读</h1>
            <p className="hero-subtitle">
              《神曲》地图、整歌对读与知识图谱 | Digital Dante Museum
            </p>
            <blockquote>{data.manifest.hero.quote}</blockquote>
          </article>

          <article className="info-card">
            <p className="eyebrow">站点导览</p>
            <h2>从三界总图进入，再回到人物、篇歌与注释。</h2>
            <p>
              首页以三联总图进入地狱、炼狱与天堂。进入任一世界后，左侧是歌序目录，中间是二维地图与人物事件节点，右侧则是可切换
              1 到 4 栏的整歌对读阅读器。
            </p>
            <div className="hero-actions">
              <Link className="primary-link" to="/map">
                进入神曲阅读
              </Link>
              <Link className="secondary-link" to="/graph">
                浏览知识图谱
              </Link>
            </div>
          </article>

          <article className="info-card">
            <p className="eyebrow">规模</p>
            <ul className="stat-list">
              <li>100 歌完整正文</li>
              <li>{data.manifest.counts.works} 个版本收录</li>
              <li>{data.manifest.counts.entities} 个实体词条</li>
              <li>{data.manifest.counts.graphNodes} 个图谱节点</li>
            </ul>
          </article>
        </div>

        <article className="hero-panel hero-panel-compact home-hero-figure" style={heroMediaStyle}>
          <div className="hero-media hero-media-fill">
            <ArtworkImage
              alt={heroIllustration.title}
              fallbackSrc={data.mapScenes.overview.layers[0].image.src}
              src={heroIllustration.src}
            />
          </div>
        </article>
      </section>

      <section className="home-overview-row">
        <OverviewTriptych
          onSelectLayer={setSelectedLayer}
          scene={data.mapScenes.overview}
          selectedLayer={selectedLayer}
        />
      </section>
    </div>
  )
}
