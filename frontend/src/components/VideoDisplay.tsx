import React, { useEffect } from 'react'

interface Props {
  canvasRef: React.RefObject<HTMLCanvasElement>
  isStreaming: boolean
  framesSent?: number
  onStart: () => void
  onStop: () => void
  width?: number
  height?: number
}

export function VideoDisplay({ canvasRef, isStreaming, framesSent = 0, onStart, onStop, width = 640, height = 480 }: Props) {
  useEffect(() => {
    if (!isStreaming && canvasRef.current) {
      const ctx = canvasRef.current.getContext('2d')
      ctx?.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height)
    }
  }, [isStreaming])

  return (
    <div className="video-panel card">
      <div className="video-canvas-wrap">
        <canvas ref={canvasRef} width={width} height={height} />

        {!isStreaming && (
          <div className="video-idle">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M15 10l4.553-2.069A1 1 0 0121 8.87v6.26a1 1 0 01-1.447.9L15 14M3 8a2 2 0 012-2h10a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
            </svg>
            <span className="video-idle-text">Camera feed will appear here</span>
          </div>
        )}

        {isStreaming && (
          <div className="live-badge">
            <span className="live-dot" />
            LIVE
          </div>
        )}
      </div>

      <div className="video-footer">
        <div className="video-controls">
          <button className="btn btn-start" onClick={onStart} disabled={isStreaming}>
            <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
              <path d="M2 1.5l9 4.5-9 4.5V1.5z" />
            </svg>
            Start
          </button>
          <button className="btn btn-stop" onClick={onStop} disabled={!isStreaming}>
            <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor">
              <rect x="1" y="1" width="8" height="8" rx="1" />
            </svg>
            Stop
          </button>
        </div>

        <div className="video-footer-stats">
          <span className="video-footer-label">Frames sent</span>
          <span className="video-footer-value">{framesSent}</span>
        </div>
      </div>
    </div>
  )
}
