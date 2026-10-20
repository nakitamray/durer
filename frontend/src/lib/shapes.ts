import rough from 'roughjs'
import type { Shape } from './types'
import type { Stroke } from './sketch'

const gen = rough.generator()

function dist(a: [number, number], b: [number, number]) {
  return Math.hypot(a[0] - b[0], a[1] - b[1])
}

export function describe(s: Shape): string {
  if (s.kind === 'ellipse') {
    const ratio = Math.min(s.rx!, s.ry!) / Math.max(s.rx!, s.ry!)
    return ratio > 0.88 ? 'circle' : 'oval'
  }
  if (s.kind === 'box') {
    const [a, b, c] = s.points!
    const ratio = Math.min(dist(a, b), dist(b, c)) / Math.max(dist(a, b), dist(b, c))
    return ratio > 0.88 ? 'square' : 'rectangle'
  }
  if (s.kind === 'triangle') return 'triangle'
  return `${s.points!.length}-sided shape`
}

// rough.js wobble is in drawing units, so draw at the size the api measured
// and let the svg transform scale it up
export function outline(s: Shape, seed: number, width: number): Stroke[] {
  const opts = { roughness: 1.1, bowing: 1.2, seed, preserveVertices: false }
  const d =
    s.kind === 'ellipse'
      ? gen.ellipse(s.cx!, s.cy!, s.rx! * 2, s.ry! * 2, opts)
      : gen.polygon(s.points!, opts)
  return gen.toPaths(d).map((p) => ({ d: p.d, stroke: 'currentColor', width }))
}
