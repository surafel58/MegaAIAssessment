import { useRef } from 'react'
import { useWebcamCapture } from './hooks/useWebcamCapture'
import { useVideoStream } from './hooks/useVideoStream'
import { VideoDisplay } from './components/VideoDisplay'
import { ConfidenceRing } from './components/ConfidenceRing'
import { DetectionLog } from './components/DetectionLog'
import { ThemeToggle } from './components/ThemeToggle'
import { InfoTooltip } from './components/InfoTooltip'

export default function App() {
  const sessionIdRef = useRef<string>(crypto.randomUUID())
  const sessionId = sessionIdRef.current
  const shortId = '#' + sessionId.slice(0, 8)

  const { videoRef, isStreaming, error, stats, start, stop } = useWebcamCapture(sessionId)
  const { canvasRef, isConnected: isStreamConnected } = useVideoStream(sessionId, isStreaming)

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="brand">
          <img
            src="/logo.png"
            alt="FaceStream"
            className={`brand-logo${isStreaming ? ' live' : ''}`}
          />
          <span className="brand-name">FaceStream</span>
        </div>

        <span className="session-badge">{shortId}</span>

        <div className="header-status">
          <span className={`status-dot${isStreamConnected ? ' active' : ''}`} />
          {isStreamConnected ? 'Stream connected' : 'Disconnected'}
        </div>

        <div className="header-actions">
          <ThemeToggle />
        </div>
      </header>

      {/* Hidden video element for frame capture */}
      <video ref={videoRef} style={{ display: 'none' }} muted playsInline />

      {/* Main grid */}
      <main className="main-content">
        {/* Video column */}
        <VideoDisplay
          canvasRef={canvasRef}
          isStreaming={isStreaming}
          framesSent={stats.framesSent}
          onStart={start}
          onStop={stop}
        />

        {/* Sidebar */}
        <aside className="sidebar">
          {/* Metrics */}
          <div className="metric-grid">
            <div className="metric-item">
              <div className="metric-item-header">
                <div className="metric-label">Frames</div>
                <InfoTooltip text="Total JPEG frames sent from your camera to the server this session." />
              </div>
              <div className="metric-value">{stats.framesSent}</div>
            </div>
            <div className="metric-item">
              <div className="metric-item-header">
                <div className="metric-label">Faces</div>
                <InfoTooltip text="Number of frames where at least one face was detected by the MediaPipe model." />
              </div>
              <div className="metric-value accent">{stats.facesDetected}</div>
            </div>
          </div>

          {/* Confidence ring */}
          <ConfidenceRing confidence={stats.lastConfidence} />

          {/* Detection log */}
          <DetectionLog sessionId={sessionId} active={isStreaming} />
        </aside>
      </main>

      {error && (
        <div className="error-banner">{error}</div>
      )}
    </div>
  )
}
