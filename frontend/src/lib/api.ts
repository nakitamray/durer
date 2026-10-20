import type { Grid, Paper, ShapeStudy, ValueStudy } from './types'

const BASE = import.meta.env.VITE_API_URL || '/api'

const MARGIN = { in: 0.5, cm: 1.5 }

async function post(path: string, file: File, fields: Record<string, string | number>) {
  const form = new FormData()
  form.append('image', file)
  for (const [k, v] of Object.entries(fields)) form.append(k, String(v))

  let res: Response
  try {
    res = await fetch(BASE + path, { method: 'POST', body: form })
  } catch {
    throw new Error("Can't reach the server. Is the API running?")
  }
  if (!res.ok) {
    const body = await res.json().catch(() => null)
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

export async function getShapes(file: File, simplicity: number): Promise<ShapeStudy> {
  const res = await post('/shapes', file, { simplicity })
  return res.json()
}

export async function getContour(file: File, detail: number): Promise<string> {
  const res = await post('/contour', file, { detail })
  return URL.createObjectURL(await res.blob())
}

export async function getValues(file: File, levels: number): Promise<ValueStudy> {
  const res = await post('/values', file, { levels })
  return res.json()
}

export async function getPdf(file: File, paper: Paper, cols: number): Promise<Blob> {
  const res = await post('/export', file, paperFields(paper, cols))
  return res.blob()
}
