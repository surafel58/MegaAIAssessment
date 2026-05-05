import { InfoTooltip } from './InfoTooltip'

interface Props {
  confidence: number
}

const R = 46
const CX = 65
const CY = 65
const CIRCUMFERENCE = 2 * Math.PI * R
const ARC = CIRCUMFERENCE * 0.75

export function ConfidenceRing({ confidence }: Props) {
  const clipped = Math.max(0, Math.min(1, confidence))
  const filled = ARC * clipped
  const empty = CIRCUMFERENCE - filled
  const pct = Math.round(clipped * 100)

  return (
    <div className="confidence-card">
      <div className="confidence-card-header">
        <div className="confidence-title">Last Confidence</div>
        <InfoTooltip text="Detection confidence score (0–100%) of the most recently processed frame. Higher means the model is more certain a face is present." />
      </div>
      <div className="ring-wrap">
        <svg
          viewBox="0 0 130 130"
          width="130"
          height="130"
          style={{ overflow: 'visible' }}
        >
          <g transform={`rotate(135, ${CX}, ${CY})`}>
            {/* Track */}
            <circle
              cx={CX}
              cy={CY}
              r={R}
              fill="none"
              stroke="var(--ring-track)"
              strokeWidth={8}
              strokeDasharray={`${ARC} ${CIRCUMFERENCE - ARC}`}
              strokeLinecap="round"
            />
            {/* Fill */}
            {clipped > 0 && (
              <circle
                cx={CX}
                cy={CY}
                r={R}
                fill="none"
                stroke="url(#ringGrad)"
                strokeWidth={8}
                strokeDasharray={`${filled} ${empty}`}
                strokeLinecap="round"
                style={{ transition: 'stroke-dasharray 0.5s ease' }}
              />
            )}
          </g>
          <defs>
            <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#818CF8" />
              <stop offset="100%" stopColor="#4F46E5" />
            </linearGradient>
          </defs>
        </svg>
        <div className="ring-center">
          <span className="ring-pct">{pct}</span>
          <span className="ring-sub">percent</span>
        </div>
      </div>
    </div>
  )
}
