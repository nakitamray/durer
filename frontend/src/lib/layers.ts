import { line, type Stroke } from './sketch'
import type { BlockIn, Point } from './types'

type Seg = [Point, Point]

function sides(poly: Point[]): Seg[] {
  return poly.map((p, i) => [p, poly[(i + 1) % poly.length]] as Seg)
}

// a segment pushed past both ends, the way construction lines overshoot
function overshoot([a, b]: Seg, amount: number): Seg {
  const dx = b[0] - a[0]
  const dy = b[1] - a[1]
  return [
    [a[0] - dx * amount, a[1] - dy * amount],
    [b[0] + dx * amount, b[1] + dy * amount],
  ]
}

export interface Layer {
  strokes: Stroke[]
  faint: Stroke[]
}

export function placementLayer(b: BlockIn): Layer {
  const [x0, y0, x1, y1] = b.placement.box
  const w = x1 - x0
  const h = y1 - y0
  const [cx, cy] = b.placement.center
  const tick = Math.max(w, h) * 0.12
  const strokes = [
    // top and bottom
    ...line(cx - tick, y0, cx + tick, y0, { seed: 1, width: 1.6 }),
    ...line(cx - tick, y1, cx + tick, y1, { seed: 2, width: 1.6 }),
    // left and right
    ...line(x0, cy - tick, x0, cy + tick, { seed: 3, width: 1.6 }),
    ...line(x1, cy - tick, x1, cy + tick, { seed: 4, width: 1.6 }),
  ]
  const [[ax, ay], [bx, by]] = b.placement.axis
  const faint = [
    ...line(ax, ay, bx, by, { seed: 5, width: 1, roughness: 1.2 }),
    // halfway marks
    ...line(x0 - tick * 0.3, (y0 + y1) / 2, x0 + tick * 0.3, (y0 + y1) / 2, { seed: 6, width: 1 }),
    ...line((x0 + x1) / 2, y1 - tick * 0.3, (x0 + x1) / 2, y1 + tick * 0.3, { seed: 7, width: 1 }),
  ]
  return { strokes, faint }
}

export function bigLayer(b: BlockIn): Layer {
  const strokes: Stroke[] = []
  const faint: Stroke[] = []
  let seed = 10
  for (const poly of b.big) {
    for (const seg of sides(poly)) {
      const [[ax, ay], [bx, by]] = seg
      strokes.push(...line(ax, ay, bx, by, { seed: seed++, width: 1.5, roughness: 0.9 }))
      const [[ex, ey], [fx, fy]] = overshoot(seg, 0.12)
      faint.push(...line(ex, ey, fx, fy, { seed: seed++, width: 0.8, roughness: 1.3 }))
    }
  }
  return { strokes, faint }
}

export function mediumLayer(b: BlockIn): Layer {
  const strokes: Stroke[] = []
  const faint: Stroke[] = []
  let seed = 200
  for (const poly of b.medium) {
    for (const seg of sides(poly)) {
      const [[ax, ay], [bx, by]] = overshoot(seg, 0.04)
      strokes.push(...line(ax, ay, bx, by, { seed: seed++, width: 1.2, roughness: 0.8 }))
    }
  }
  return { strokes, faint }
}
