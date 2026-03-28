import { useState } from 'react'
import { Link } from 'react-router-dom'

import { OverviewTriptych } from '../components/overview-triptych'
import type { SiteData } from '../data-loader'

export function MapPage({ data }: { data: SiteData }) {
  const [selectedLayer, setSelectedLayer] = useState<'medieval' | 'structure'>('medieval')

  return (
    <div className="overview-layout">
      <aside className="overview-sidebar">
        <div className="sidebar-header">
          <p className="eyebrow">总图目录</p>
          <h2>神曲阅读</h2>
          <p>从总图进入三界，再从地图热点跳到具体歌与人物。</p>
        </div>
        <div className="sidebar-scroll">
          <Link className="sidebar-link-card" to="/inferno">
            <strong>地狱篇</strong>
            <small>从黑暗森林进入九圈与科库托斯</small>
          </Link>
          <Link className="sidebar-link-card" to="/purgatorio">
            <strong>炼狱篇</strong>
            <small>从海岸、山门到地上乐园</small>
          </Link>
          <Link className="sidebar-link-card" to="/paradiso">
            <strong>天堂篇</strong>
            <small>从月球天一路上升到白色玫瑰</small>
          </Link>
          <Link className="sidebar-link-card" to="/graph">
            <strong>知识图谱</strong>
            <small>按人物、地点、事件与概念展开关系网</small>
          </Link>
        </div>
      </aside>

      <section className="overview-main">
        <OverviewTriptych
          onSelectLayer={setSelectedLayer}
          scene={data.mapScenes.overview}
          selectedLayer={selectedLayer}
        />
      </section>
    </div>
  )
}
