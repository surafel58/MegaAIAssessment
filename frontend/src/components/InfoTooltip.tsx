interface Props {
  text: string
}

export function InfoTooltip({ text }: Props) {
  return (
    <div className="info-tooltip-wrap">
      <button className="info-icon" aria-label="Info" tabIndex={0}>
        <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
          <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" />
          <path d="M8 7v5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <circle cx="8" cy="4.5" r="0.75" fill="currentColor" />
        </svg>
      </button>
      <div className="info-tooltip" role="tooltip">
        <div className="info-tooltip-inner">{text}</div>
      </div>
    </div>
  )
}
