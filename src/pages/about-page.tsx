import type { SiteData } from '../data-loader'

export function AboutPage({ data }: { data: SiteData }) {
  return (
    <div className="stack-page">
      <section className="essay-card about-hero-card">
        <p className="eyebrow">神曲导读</p>
        <h1>为什么《神曲》仍然重要</h1>
        <p className="hero-subtitle">
          《神曲》不仅是一部宗教作品，也是一场关于语言、道德、政治与人性的宏大实验。它把中世纪宇宙秩序写成可行走的地图，又把私人流亡经验锻造成文明尺度的诗歌。
        </p>
        <p>
          这一页以你提供的读书笔记为基础，重新组织《神曲》的形式特征、思想背景与文学价值：先看百歌结构和数字秩序，再看三行连锁韵、十一音节诗行与托斯卡纳俗语写作，最后回到“为什么它叫喜剧”、为什么它既是中世纪的终章，也是通向现代意识的开端。
        </p>
      </section>

      <section className="essay-grid about-sections-grid">
        {data.aboutPage.sections.map((section) => (
          <article className="essay-card" key={section.title}>
            <h2>{section.title}</h2>
            <p>{section.body}</p>
          </article>
        ))}
      </section>
    </div>
  )
}
