import { useEffect, useRef, useState, useCallback } from 'react'

export interface CaptureStats {
  framesSent: number
  facesDetected: number
  lastConfidence: number
}

export interface UseCaptureResult {
  videoRef: React.RefObject<HTMLVideoElement>
  isStreaming: boolean
  error: string | null
  stats: CaptureStats
  start: () => void
  stop: () => void
}

const WS_URL = import.meta.env.VITE_WS_URL ?? ''

export function useWebcamCapture(sessionId: string): UseCaptureResult {
  const videoRef = useRef<HTMLVideoElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<CaptureStats>({
    framesSent: 0,
    facesDetected: 0,
    lastConfidence: 0,
  })

  const stop = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    if (wsRef.current) wsRef.current.close()
    if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop())
    setIsStreaming(false)
  }, [])

  const start = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' },
      })
      streamRef.current = stream

      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      }

      const ws = new WebSocket(`${WS_URL}/ws/ingest?session_id=${sessionId}`)
      ws.binaryType = 'arraybuffer'
      wsRef.current = ws

      const canvas = document.createElement('canvas')
      canvas.width = 640
      canvas.height = 480
      canvasRef.current = canvas
      const ctx = canvas.getContext('2d')!

      ws.onopen = () => {
        setIsStreaming(true)
        setError(null)

        intervalRef.current = setInterval(() => {
          if (!videoRef.current || ws.readyState !== WebSocket.OPEN) return
          ctx.drawImage(videoRef.current, 0, 0, 640, 480)
          canvas.toBlob(blob => {
            if (!blob || ws.readyState !== WebSocket.OPEN) return
            blob.arrayBuffer().then(buf => ws.send(buf))
          }, 'image/jpeg', 0.8)
        }, 1000 / 15)
      }

      ws.onmessage = (evt) => {
        try {
          const ack = JSON.parse(evt.data as string)
          setStats(prev => ({
            framesSent: prev.framesSent + 1,
            facesDetected: prev.facesDetected + (ack.detected ? 1 : 0),
            lastConfidence: ack.confidence ?? 0,
          }))
        } catch {
          // ignore malformed ack
        }
      }

      ws.onerror = () => setError('Ingest WebSocket error')
      ws.onclose = () => {
        setIsStreaming(false)
        if (intervalRef.current) clearInterval(intervalRef.current)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to access webcam')
    }
  }, [sessionId])

  useEffect(() => () => stop(), [stop])

  return { videoRef, isStreaming, error, stats, start, stop }
}
