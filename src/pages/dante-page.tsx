import { ArtworkImage } from '../components/artwork-image'
import type { SiteData } from '../data-loader'

export function DantePage({ data }: { data: SiteData }) {
  const [mainIllustration] = data.dantePage.illustrations
  const portraitStyle =
    mainIllustration?.width && mainIllustration?.height
      ? { aspectRatio: `${mainIllustration.width} / ${mainIllustration.height}` }
      : undefined

  return (
    <div className="stack-page">
      <section className="book-hero book-hero-text-first">
        <div className="book-hero-copy">
          <p className="eyebrow">但丁其人</p>
          <h1>但丁：把流亡写成宇宙的人</h1>
          <p className="hero-subtitle">
            从佛罗伦萨城邦政治、黑白党争、贝雅特丽齐的精神形象，到永久流放后的自我辩护，《神曲》把私人命运推进为一部灵魂史诗。
          </p>

          <div className="book-hero-grid">
            <article className="essay-card">
              <p className="eyebrow">生平时间线</p>
              <div className="timeline-list compact">
                {data.dantePage.timeline.slice(0, 3).map((item) => (
                  <div className="timeline-item" key={`${item.year}-${item.title}`}>
                    <strong>{item.year}</strong>
                    <div>
                      <h3>{item.title}</h3>
                      <p>{item.body}</p>
                    </div>
                  </div>
                ))}
              </div>
            </article>

            <article className="essay-card">
              <p className="eyebrow">写作动因</p>
              {data.dantePage.sections.map((section) => (
                <div className="essay-block" key={section.title}>
                  <h3>{section.title}</h3>
                  <p>{section.body}</p>
                </div>
              ))}
            </article>
          </div>
        </div>

        <article
          className="essay-card illustrated portrait-card portrait-card-hero portrait-card-aside"
          style={portraitStyle}
        >
          <div className="hero-media hero-media-fill">
            <ArtworkImage alt={mainIllustration.title} src={mainIllustration.src} />
          </div>
        </article>
      </section>

      <section className="essay-card">
        <p className="eyebrow">完整时间线</p>
        <div className="timeline-list">
          {data.dantePage.timeline.map((item) => (
            <div className="timeline-item" key={`${item.year}-${item.title}`}>
              <strong>{item.year}</strong>
              <div>
                <h3>{item.title}</h3>
                <p>{item.body}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
