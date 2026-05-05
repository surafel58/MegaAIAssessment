import { useEffect, useState } from 'react'
import { fetchRoi, RoiRecord } from '../api/roiClient'

interface Props {
  sessionId: string
  active: boolean
}

export function RoiTable({ sessionId, active }: Props) {
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

  if (!active) return null

  return (
    <div style={{ marginTop: 16 }}>
      <h3 style={{ margin: '0 0 8px', fontSize: 14, color: '#aaa' }}>
        ROI Detections — {total} total
      </h3>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ background: '#1a1a1a', color: '#888' }}>
              <th style={th}>Frame</th>
              <th style={th}>Time</th>
              <th style={th}>X</th>
              <th style={th}>Y</th>
              <th style={th}>W</th>
              <th style={th}>H</th>
              <th style={th}>Conf</th>
            </tr>
          </thead>
          <tbody>
            {records.map(r => (
              <tr key={r.id} style={{ borderBottom: '1px solid #222' }}>
                <td style={td}>{r.frame_number}</td>
                <td style={td}>{new Date(r.timestamp).toLocaleTimeString()}</td>
                <td style={td}>{r.bbox.x.toFixed(0)}</td>
                <td style={td}>{r.bbox.y.toFixed(0)}</td>
                <td style={td}>{r.bbox.width.toFixed(0)}</td>
                <td style={td}>{r.bbox.height.toFixed(0)}</td>
                <td style={{ ...td, color: '#00ff41' }}>{(r.confidence * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
        {records.length === 0 && (
          <p style={{ color: '#555', textAlign: 'center', padding: 16 }}>No detections yet</p>
        )}
      </div>
    </div>
  )
}

const th: React.CSSProperties = {
  padding: '6px 10px',
  textAlign: 'left',
  fontWeight: 600,
}
const td: React.CSSProperties = {
  padding: '5px 10px',
  color: '#ccc',
}
