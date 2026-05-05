import { CaptureStats } from '../hooks/useWebcamCapture'

interface Props {
  isStreaming: boolean
  isStreamConnected: boolean
  stats: CaptureStats
  error: string | null
}

export function StatusBar({ isStreaming, isStreamConnected, stats, error }: Props) {
  const dot = (on: boolean, label: string) => (
    <span style={{ marginRight: 16 }}>
      <span style={{
        display: 'inline-block',
        width: 8, height: 8,
        borderRadius: '50%',
        background: on ? '#00ff41' : '#555',
        marginRight: 5,
      }} />
      {label}
    </span>
  )

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      padding: '8px 12px',
      background: '#1a1a1a',
      borderRadius: 4,
      fontSize: 13,
      gap: 8,
      flexWrap: 'wrap',
    }}>
      {dot(isStreaming, 'Ingest')}
      {dot(isStreamConnected, 'Stream')}
      <span style={{ color: '#888', marginRight: 16 }}>
        Frames: <strong style={{ color: '#ccc' }}>{stats.framesSent}</strong>
      </span>
      <span style={{ color: '#888', marginRight: 16 }}>
        Faces: <strong style={{ color: '#00ff41' }}>{stats.facesDetected}</strong>
      </span>
      {stats.lastConfidence > 0 && (
        <span style={{ color: '#888' }}>
          Last conf: <strong style={{ color: '#ccc' }}>{(stats.lastConfidence * 100).toFixed(1)}%</strong>
        </span>
      )}
      {error && <span style={{ color: '#ff4444', marginLeft: 'auto' }}>{error}</span>}
    </div>
  )
}
