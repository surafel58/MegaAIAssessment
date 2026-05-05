import { useEffect, useState } from 'react'
import { fetchRoi, RoiRecord } from '../api/roiClient'
import { InfoTooltip } from './InfoTooltip'

interface Props {
  sessionId: string
  active: boolean
}

export function DetectionLog({ sessionId, active }: Props) {
  const [records, setRecords] = useState<RoiRecord[]>([])
  const [total, setTotal] = useState(0)

  useEffect(() => {
    if (!active) return
    const poll = async () => {
      try {
        const page = await fetchRoi(sessionId, 20)
        setRecords(page.items)
        setTotal(page.total)
      } catch {
        // ignore transient errors
      }
    }
    poll()
    const id = setInterval(poll, 2000)
    return () => clearInterval(id)
  }, [sessionId, active])

  return (
    <div className="log-card">
      <div className="log-header">
        <span className="log-title">Detections</span>
        {active && <span className="log-count">{total} total</span>}
        <InfoTooltip text="Face detection records stored in the database, polled every 2 s. Each row shows the frame number, timestamp, and confidence score." />
      </div>
      <div className="log-list">
        {records.length === 0 ? (
          <div className="log-empty">
            {active ? 'Waiting for faces…' : 'Start streaming to see detections'}
          </div>
        ) : (
          records.map(r => (
            <div className="log-item" key={r.id}>
              <div className="log-item-header">
                <span className="log-frame">#{String(r.frame_number).padStart(4, '0')}</span>
                <span className="log-time">{new Date(r.timestamp).toLocaleTimeString()}</span>
              </div>
              <div className="log-bar-wrap">
                <div className="log-bar-track">
                  <div
                    className="log-bar-fill"
                    style={{ width: `${r.confidence * 100}%` }}
                  />
                </div>
                <span className="log-pct">{(r.confidence * 100).toFixed(1)}%</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
