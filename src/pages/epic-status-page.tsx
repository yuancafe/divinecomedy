import type { SiteData } from '../data-loader'

const DIMENSION_KEY = '对比维度'
const HIGHLIGHT_WORK = '神曲'

function cleanValue(value: string | undefined) {
  return value?.trim() ?? ''
}

export function EpicStatusPage({ data }: { data: SiteData }) {
  const rows = data.epicComparisons
  const works = rows.length > 0 ? Object.keys(rows[0]).filter((key) => key !== DIMENSION_KEY) : []
  const summaryRows = rows.filter((row) => ['作者与年代', '性质与起源', '核心主题', '核心创新'].includes(row[DIMENSION_KEY]))
  const detailRows = rows.filter((row) => !summaryRows.some((item) => item[DIMENSION_KEY] === row[DIMENSION_KEY]))

  return (
    <div className="stack-page">
      <section className="section-heading page-intro epic-page-intro">
        <div>
          <p className="eyebrow">史诗谱系</p>
          <h1>《神曲》在西方史诗中的位置</h1>
        </div>
        <p>
          从荷马到维吉尔，从塔索、弥尔顿到歌德、乔伊斯，《神曲》站在古典史诗与现代主体经验之间，把史诗从英雄远征转向灵魂远行。
        </p>
      </section>

      <section className="epic-summary-grid">
        {summaryRows.map((row) => (
          <article className="essay-card epic-summary-card" key={row[DIMENSION_KEY]}>
            <p className="eyebrow">{row[DIMENSION_KEY]}</p>
            <div className="epic-summary-copy">
              {works.map((work) => (
                <div
                  className={work === HIGHLIGHT_WORK ? 'epic-summary-line epic-summary-line-active' : 'epic-summary-line'}
                  key={`${row[DIMENSION_KEY]}-${work}`}
                >
                  <strong>{work}</strong>
                  <span>{cleanValue(row[work])}</span>
                </div>
              ))}
            </div>
          </article>
        ))}
      </section>

      <section className="comparison-table-shell epic-table-shell">
        <div className="comparison-callout epic-table-callout">
          <p className="eyebrow">对比阅读</p>
          <h2>把《神曲》放回西方史诗长链中</h2>
          <p>左侧是维度，右侧依次比较代表作品；《神曲》列固定高亮，帮助快速看到它在主题、体裁、语言与世界观上的转折位置。</p>
        </div>

        <table className="comparison-table epic-comparison-table">
          <thead>
            <tr>
              <th scope="col">{DIMENSION_KEY}</th>
              {works.map((work) => (
                <th className={work === HIGHLIGHT_WORK ? 'epic-work-head epic-work-head-active' : 'epic-work-head'} key={work} scope="col">
                  {work}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {detailRows.map((row) => (
              <tr key={row[DIMENSION_KEY]}>
                <th scope="row">{row[DIMENSION_KEY]}</th>
                {works.map((work) => (
                  <td className={work === HIGHLIGHT_WORK ? 'epic-cell epic-cell-active' : 'epic-cell'} key={`${row[DIMENSION_KEY]}-${work}`}>
                    {cleanValue(row[work])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}
