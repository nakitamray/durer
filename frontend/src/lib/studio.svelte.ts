import * as api from './api'
import { PAPERS } from './papers'
import type {
  BlockIn,
  Cell,
  ContourStudy,
  Grid,
  Notan,
  Paper,
  ShapeStudy,
  ValueStudy,
} from './types'

export const STEPS = [
  { key: 'setup', numeral: 'I', name: 'Mise en place', sub: 'the subject and paper' },
  { key: 'grid', numeral: 'II', name: 'La grille', sub: 'boxing it in' },
  { key: 'place', numeral: 'III', name: "L'emplacement", sub: 'where it sits' },
  { key: 'big', numeral: 'IV', name: 'Grandes formes', sub: 'big shapes' },
  { key: 'medium', numeral: 'V', name: 'Formes moyennes', sub: 'medium shapes' },
  { key: 'notan', numeral: 'VI', name: 'Le notan', sub: 'light and shadow' },
  { key: 'contour', numeral: 'VII', name: 'Le contour', sub: 'the real lines' },
  { key: 'values', numeral: 'VIII', name: 'Les valeurs', sub: 'modeling the tones' },
] as const

export type StepKey = (typeof STEPS)[number]['key']

type Job = 'grid' | 'blockin' | 'shapes' | 'notan' | 'contour' | 'values'

class Studio {
  file = $state<File | null>(null)
  src = $state<string | null>(null)
  size = $state({ w: 0, h: 0 })

  step = $state(0)
  current: StepKey = $derived(STEPS[this.step].key)

  paper = $state<Paper>(PAPERS[2])
  cols = $state(6)
  grid = $state<Grid | null>(null)
  showGrid = $state(true)
  refOpacity = $state(1)
  ghost = $state(true)
  cell = $state<Cell | null>(null)

  blockin = $state<BlockIn | null>(null)
  solids = $state(false)
  simplicity = $state(3)
  shapes = $state<ShapeStudy | null>(null)

  bias = $state(3)
  hatched = $state(true)
  notan = $state<Notan | null>(null)

  detail = $state(3)
  contour = $state<ContourStudy | null>(null)

  levels = $state(4)
  values = $state<ValueStudy | null>(null)

  loading = $state(false)
  error = $state<string | null>(null)

  // each result is cached under the settings that produced it, and each kind
  // of request has a counter so a slow old answer can't overwrite a newer one
  private keys: Partial<Record<Job, string>> = {}
  private latest: Record<Job, number> = {
    grid: 0,
    blockin: 0,
    shapes: 0,
    notan: 0,
    contour: 0,
    values: 0,
  }
  private pending = 0

  async load(file: File) {
    const src = URL.createObjectURL(file)
    const img = new Image()
    img.src = src
    try {
      await img.decode()
    } catch {
      URL.revokeObjectURL(src)
      this.error = "That file doesn't look like an image."
      return
    }

    this.clear()
    this.file = file
    this.src = src
    this.size = { w: img.naturalWidth, h: img.naturalHeight }
    // turn the paper to match the subject
    this.paper = orient(this.paper, img.naturalWidth > img.naturalHeight)
  }

  reset() {
    this.clear()
    this.file = null
    this.step = 0
  }

  private clear() {
    if (this.src) URL.revokeObjectURL(this.src)
    this.src = null
    this.grid = this.cell = null
    this.blockin = this.shapes = this.notan = this.contour = this.values = null
    this.keys = {}
    this.error = null
    // anything still in flight belongs to the old image
    for (const k of Object.keys(this.latest) as Job[]) this.latest[k]++
  }

  setPaper(p: Paper) {
    this.paper = orient(p, this.size.w > this.size.h)
  }

  rotatePaper() {
    this.paper = { ...this.paper, width: this.paper.height, height: this.paper.width }
  }

  refreshGrid() {
    return this.fetch('grid', `${this.paper.label}:${this.paper.width}:${this.cols}`, async (f) => {
      const grid = await api.getGrid(f, this.paper, this.cols)
      return () => {
        this.grid = grid
        if (this.cell && (this.cell.col >= grid.cols || this.cell.row >= grid.rows)) {
          this.cell = null
        }
      }
    })
  }

  refreshBlockIn() {
    return this.fetch('blockin', '', async (f) => {
      const b = await api.getBlockIn(f)
      return () => (this.blockin = b)
    })
  }

  refreshShapes() {
    return this.fetch('shapes', `${this.simplicity}`, async (f) => {
      const s = await api.getShapes(f, this.simplicity)
      return () => (this.shapes = s)
    })
  }

  refreshNotan() {
    return this.fetch('notan', `${this.bias}`, async (f) => {
      const n = await api.getNotan(f, this.bias)
      return () => (this.notan = n)
    })
  }

  refreshContour() {
    return this.fetch('contour', `${this.detail}`, async (f) => {
      const c = await api.getContour(f, this.detail)
      return () => (this.contour = c)
    })
  }

  refreshValues() {
    return this.fetch('values', `${this.levels}`, async (f) => {
      const v = await api.getValues(f, this.levels)
      return () => (this.values = v)
    })
  }

  async downloadPdf() {
    if (!this.file) return
    this.pending++
    this.loading = true
    try {
      const blob = await api.getPdf(this.file, this.paper, this.cols)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'durer-grid.pdf'
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      this.error = e instanceof Error ? e.message : String(e)
    } finally {
      this.loading = --this.pending > 0
    }
  }

  private async fetch(job: Job, key: string, run: (f: File) => Promise<() => void>) {
    if (!this.file || this.keys[job] === key) return
    const n = ++this.latest[job]
    this.pending++
    this.loading = true
    this.error = null
    try {
      const apply = await run(this.file)
      if (n !== this.latest[job]) return
      apply()
      this.keys[job] = key
    } catch (e) {
      if (n === this.latest[job]) this.error = e instanceof Error ? e.message : String(e)
    } finally {
      this.loading = --this.pending > 0
    }
  }
}

function orient(p: Paper, landscape: boolean): Paper {
  const long = Math.max(p.width, p.height)
  const short = Math.min(p.width, p.height)
  return landscape ? { ...p, width: long, height: short } : { ...p, width: short, height: long }
}

export const studio = new Studio()
