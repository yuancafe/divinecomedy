import type { ReactNode } from 'react'

interface HeroPanelProps {
  eyebrow: string
  title: string
  subtitle: string
  quote?: string
  media?: ReactNode
}

export function HeroPanel({ eyebrow, title, subtitle, quote, media }: HeroPanelProps) {
  return (
    <section className="hero-panel">
      <div className="hero-copy">
        <p className="hero-eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="hero-subtitle">{subtitle}</p>
        {quote ? <blockquote>{quote}</blockquote> : null}
      </div>
      {media ? <div className="hero-media">{media}</div> : null}
    </section>
  )
}
