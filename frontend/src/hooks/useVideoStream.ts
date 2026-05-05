import { useEffect, useRef, useState } from 'react'

export interface UseStreamResult {
  canvasRef: React.RefObject<HTMLCanvasElement>
  isConnected: boolean
}

const WS_URL = import.meta.env.VITE_WS_URL ?? ''

export function useVideoStream(sessionId: string, active: boolean): UseStreamResult {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    if (!active) return

    const ws = new WebSocket(`${WS_URL}/ws/stream?session_id=${sessionId}`)
    ws.binaryType = 'arraybuffer'
    wsRef.current = ws

    ws.onopen = () => setIsConnected(true)
    ws.onclose = () => setIsConnected(false)

    ws.onmessage = (evt) => {
      if (typeof evt.data === 'string') return  // JSON event (session_ended / timeout)

      const blob = new Blob([evt.data], { type: 'image/jpeg' })
      const url = URL.createObjectURL(blob)
      const img = new Image()
      img.onload = () => {
        const canvas = canvasRef.current
        if (!canvas) return
        const ctx = canvas.getContext('2d')!
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
        URL.revokeObjectURL(url)
      }
      img.src = url
    }

    return () => {
      ws.close()
      setIsConnected(false)
    }
  }, [sessionId, active])

  return { canvasRef, isConnected }
}
