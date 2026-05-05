import React from 'react'

interface Props {
  canvasRef: React.RefObject<HTMLCanvasElement>
  width?: number
  height?: number
}

export function VideoDisplay({ canvasRef, width = 640, height = 480 }: Props) {
  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        style={{
          border: '2px solid #333',
          borderRadius: 4,
          background: '#111',
          display: 'block',
          maxWidth: '100%',
        }}
      />
    </div>
  )
}
