import { useRef } from 'react'
import { useWebcamCapture } from './hooks/useWebcamCapture'
import { useVideoStream } from './hooks/useVideoStream'
import { VideoDisplay } from './components/VideoDisplay'
import { RoiTable } from './components/RoiTable'
import { StatusBar } from './components/StatusBar'

export default function App() {
  const sessionIdRef = useRef<string>(crypto.randomUUID())
  const sessionId = sessionIdRef.current

  const { videoRef, isStreaming, error, stats, start, stop } = useWebcamCapture(sessionId)
  const { canvasRef, isConnected: isStreamConnected } = useVideoStream(sessionId, isStreaming)

  return (
    <div style={{ maxWidth: 720, margin: '0 auto', padding: 24 }}>
      <h1 style={{ fontSize: 20, margin: '0 0 16px', color: '#e0e0e0', letterSpacing: 1 }}>
        Face Detection Stream
      </h1>

      <StatusBar
        isStreaming={isStreaming}
        isStreamConnected={isStreamConnected}
        stats={stats}
        error={error}
      />

      <div style={{ margin: '16px 0', display: 'flex', gap: 12 }}>
        <button
          onClick={start}
          disabled={isStreaming}
          style={btnStyle(isStreaming ? '#333' : '#00aa33')}
        >
          Start
        </button>
        <button
          onClick={stop}
          disabled={!isStreaming}
          style={btnStyle(!isStreaming ? '#333' : '#aa2200')}
        >
          Stop
        </button>
      </div>

      {/* Hidden video element — only used for frame capture */}
      <video
        ref={videoRef}
        style={{ display: 'none' }}
        muted
        playsInline
      />

      <VideoDisplay canvasRef={canvasRef} />

      <RoiTable sessionId={sessionId} active={isStreaming} />
    </div>
  )
}

function btnStyle(bg: string): React.CSSProperties {
  return {
    padding: '8px 20px',
    border: 'none',
    borderRadius: 4,
    background: bg,
    color: '#fff',
    fontSize: 14,
    cursor: 'pointer',
    transition: 'background 0.2s',
  }
}
