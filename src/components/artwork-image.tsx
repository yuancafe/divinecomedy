export function ArtworkImage({
  src,
  fallbackSrc,
  alt,
  className,
}: {
  src: string
  fallbackSrc?: string
  alt: string
  className?: string
}) {
  return (
    <img
      alt={alt}
      className={className}
      data-fallback-applied="false"
      key={src}
      loading="lazy"
      onError={(event) => {
        const target = event.currentTarget
        if (!fallbackSrc || target.dataset.fallbackApplied === 'true') return
        target.dataset.fallbackApplied = 'true'
        target.src = fallbackSrc
      }}
      src={src}
    />
  )
}
