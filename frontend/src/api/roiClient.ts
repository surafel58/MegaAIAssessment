const API_BASE = import.meta.env.VITE_API_URL ?? ''

export interface BboxData {
  x: number
  y: number
  width: number
  height: number
}

export interface RoiRecord {
  id: string
  frame_number: number
  timestamp: string
  bbox: BboxData
  confidence: number
  frame_width: number
  frame_height: number
}

export interface RoiPage {
  session_id: string
  total: number
  has_next: boolean
  items: RoiRecord[]
}

export async function fetchRoi(
  sessionId: string,
  limit = 20,
  offset = 0
): Promise<RoiPage> {
  const url = `${API_BASE}/api/roi?session_id=${sessionId}&limit=${limit}&offset=${offset}`
  const resp = await fetch(url)
  if (!resp.ok) throw new Error(`GET /api/roi failed: ${resp.status}`)
  return resp.json()
}
