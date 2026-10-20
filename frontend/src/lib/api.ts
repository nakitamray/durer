import type { BlockIn, ContourStudy, Grid, LightDark, Paper, ValueStudy } from './types'

const BASE = import.meta.env.VITE_API_URL || '/api'

const MARGIN = { in: 0.5, cm: 1.5 }

export const OFFLINE =
  "Can't reach the drawing server. Start it with .\\dev.ps1 (or check its window for an error)."

export async function healthy(): Promise<boolean> {
  try {
    const res = await fetch(BASE + '/health')
    return res.ok
  } catch {
    return false
  }
}

async function post(path: string, file: File, fields: Record<string, string | number>) {
  const form = new FormData()
  form.append('image', file)
  for (const [k, v] of Object.entries(fields)) form.append(k, String(v))

  let res: Response
  try {
    res = await fetch(BASE + path, { method: 'POST', body: form })
  } catch {
    throw new Error(OFFLINE)
  }
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    // the dev proxy answers with a bare 5xx when nothing is listening behind it
    if (!body && res.status >= 500) throw new Error(OFFLINE)
    const detail = typeof body?.detail === 'string' ? body.detail : `request failed (${res.status})`
    throw new Error(detail)
  }
  return res
}

function paperFields(paper: Paper, cols: number) {
  return {
    paper_width: paper.width,
    paper_height: paper.height,
    unit: paper.unit,
    margin: MARGIN[paper.unit],
    cols,
  }
}

export async function getGrid(file: File, paper: Paper, cols: number): Promise<Grid> {
  const res = await post('/grid', file, paperFields(paper, cols))
  return res.json()
}

export async function getBlockIn(file: File): Promise<BlockIn> {
  const res = await post('/blockin', file, {})
  return res.json()
}

export async function getLight(file: File, bias: number): Promise<LightDark> {
  const res = await post('/light', file, { bias })
  return res.json()
}

export async function getContour(file: File, detail: number): Promise<ContourStudy> {
  const res = await post('/contour', file, { detail })
  return res.json()
}

export async function getValues(file: File, levels: number): Promise<ValueStudy> {
  const res = await post('/values', file, { levels })
  return res.json()
}

export async function getPdf(file: File, paper: Paper, cols: number): Promise<Blob> {
  const res = await post('/export', file, paperFields(paper, cols))
  return res.blob()
}
