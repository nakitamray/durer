import * as api from './api'
import { PAPERS } from './papers'
import type { Cell, Grid, Paper, ValueStudy } from './types'

export const STEPS = [
  { numeral: 'I', name: 'Mise en place', sub: 'the subject & paper' },
  { numeral: 'II', name: 'La grille', sub: 'boxing it in' },
  { numeral: 'III', name: 'Le contour', sub: 'the main lines' },
  { numeral: 'IV', name: 'Les valeurs', sub: 'light to dark' },
]

class Studio {
  file = $state<File | null>(null)
  src = $state<string | null>(null)
  size = $state({ w: 0, h: 0 })

  step = $state(0)
  paper = $state<Paper>(PAPERS[2])
  cols = $state(6)
  grid = $state<Grid | null>(null)
  showGrid = $state(true)
  refOpacity = $state(1)
  cell = $state<Cell | null>(null)

  detail = $state(3)
  contour = $state<string | null>(null)
  levels = $state(4)
  values = $state<ValueStudy | null>(null)

  loading = $state(false)
  error = $state<string | null>(null)

  // results are cached by the settings that made them
  private contourKey = ''
  private valuesKey = ''
  private requestId = 0
  private latest = { grid: 0, contour: 0, values: 0 }

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

    if (this.src) URL.revokeObjectURL(this.src)
    if (this.contour) URL.revokeObjectURL(this.contour)
    this.file = file
    this.src = src
    this.size = { w: img.naturalWidth, h: img.naturalHeight }
    this.contour = null
    this.values = null
    this.contourKey = this.valuesKey = ''
    this.dropPending()
    this.grid = null
    this.cell = null
    this.error = null

    // turn the paper to match the subject
    const landscape = img.naturalWidth > img.naturalHeight
    this.paper = orient(this.paper, landscape)
  }

  setPaper(p: Paper) {
    const landscape = this.size.w > this.size.h
    this.paper = orient(p, landscape)
  }

  rotatePaper() {
    this.paper = { ...this.paper, width: this.paper.height, height: this.paper.width }
  }

  reset() {
    if (this.src) URL.revokeObjectURL(this.src)
    if (this.contour) URL.revokeObjectURL(this.contour)
    this.file = this.src = this.contour = this.values = this.grid = this.cell = null
    this.contourKey = this.valuesKey = ''
    this.dropPending()
    this.step = 0
  }

  async refreshGrid() {
    if (!this.file) return
    const n = ++this.latest.grid
    await this.run(async () => {
      const grid = await api.getGrid(this.file!, this.paper, this.cols)
      if (n !== this.latest.grid) return
      this.grid = grid
      if (this.cell && (this.cell.col >= this.grid.cols || this.cell.row >= this.grid.rows)) {
        this.cell = null
      }
    })
  }

  async refreshContour() {
    const key = `${this.src}:${this.detail}`
    if (!this.file || key === this.contourKey) return
    const n = ++this.latest.contour
    await this.run(async () => {
      const url = await api.getContour(this.file!, this.detail)
      if (n !== this.latest.contour) return URL.revokeObjectURL(url)
      if (this.contour) URL.revokeObjectURL(this.contour)
      this.contour = url
      this.contourKey = key
    })
  }

  async refreshValues() {
    const key = `${this.src}:${this.levels}`
    if (!this.file || key === this.valuesKey) return
    const n = ++this.latest.values
    await this.run(async () => {
      const values = await api.getValues(this.file!, this.levels)
      if (n !== this.latest.values) return
      this.values = values
      this.valuesKey = key
    })
  }

  async downloadPdf() {
    if (!this.file) return
    await this.run(async () => {
      const blob = await api.getPdf(this.file!, this.paper, this.cols)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'durer-grid.pdf'
      a.click()
      URL.revokeObjectURL(url)
    })
  }

  // anything still in flight belongs to the old image
  private dropPending() {
    this.latest.grid++
    this.latest.contour++
    this.latest.values++
  }

  private async run(fn: () => Promise<void>) {
    const id = ++this.requestId
    this.loading = true
    this.error = null
    try {
      await fn()
    } catch (e) {
      this.error = e instanceof Error ? e.message : String(e)
    } finally {
      if (id === this.requestId) this.loading = false
    }
  }
}

function orient(p: Paper, landscape: boolean): Paper {
  const long = Math.max(p.width, p.height)
  const short = Math.min(p.width, p.height)
  return landscape ? { ...p, width: long, height: short } : { ...p, width: short, height: long }
}

export const studio = new Studio()
