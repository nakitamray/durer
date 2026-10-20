import { line, type Stroke } from './sketch'
import type { BlockIn, Point } from './types'

export interface Layer {
  strokes: Stroke[]
  faint: Stroke[]
}

// a segment pushed past both ends, the way construction lines overshoot
function overshoot(a: Point, b: Point, amount: number): [Point, Point] {
  const dx = b[0] - a[0]
  const dy = b[1] - a[1]
  return [
    [a[0] - dx * amount, a[1] - dy * amount],
    [b[0] + dx * amount, b[1] + dy * amount],
  ]
}

export function placementLayer(b: BlockIn): Layer {
  const [x0, y0, x1, y1] = b.placement.box
  const w = x1 - x0
  const h = y1 - y0
  const [cx, cy] = b.placement.center
  const tick = Math.max(w, h) * 0.12
  const strokes = [
    // top and bottom
    ...line(cx - tick, y0, cx + tick, y0, { seed: 1, width: 1.8 }),
    ...line(cx - tick, y1, cx + tick, y1, { seed: 2, width: 1.8 }),
    // left and right
    ...line(x0, cy - tick, x0, cy + tick, { seed: 3, width: 1.8 }),
    ...line(x1, cy - tick, x1, cy + tick, { seed: 4, width: 1.8 }),
  ]
  const [[ax, ay], [bx, by]] = b.placement.axis
  const faint = [
    ...line(ax, ay, bx, by, { seed: 5, width: 1, roughness: 1.2 }),
    // faint box joining the marks, and the halfway marks
    ...line(x0, y0, x1, y0, { seed: 8, width: 0.6, roughness: 1.4 }),
    ...line(x0, y1, x1, y1, { seed: 9, width: 0.6, roughness: 1.4 }),
    ...line(x0, y0, x0, y1, { seed: 10, width: 0.6, roughness: 1.4 }),
    ...line(x1, y0, x1, y1, { seed: 11, width: 0.6, roughness: 1.4 }),
    ...line(x0 - tick * 0.3, (y0 + y1) / 2, x0 + tick * 0.3, (y0 + y1) / 2, { seed: 6, width: 1 }),
    ...line((x0 + x1) / 2, y1 - tick * 0.3, (x0 + x1) / 2, y1 + tick * 0.3, { seed: 7, width: 1 }),
  ]
  return { strokes, faint }
}

// straight block-in lines: each segment drawn on its own, and the longer
// ones run a little past their ends like construction lines
export function linesLayer(polylines: Point[][], width: number, seedBase: number, reach = 0.1): Layer {
  const strokes: Stroke[] = []
  const faint: Stroke[] = []
  let seed = seedBase
  for (const poly of polylines) {
    for (let i = 0; i < poly.length - 1; i++) {
      const [a, b] = [poly[i], poly[i + 1]]
      strokes.push(...line(a[0], a[1], b[0], b[1], { seed: seed++, width, roughness: 0.7 }))
      if (Math.hypot(b[0] - a[0], b[1] - a[1]) > 25) {
        const [[ex, ey], [fx, fy]] = overshoot(a, b, reach)
        faint.push(...line(ex, ey, fx, fy, { seed: seed++, width: width * 0.5, roughness: 1.2 }))
      }
    }
  }
  return { strokes, faint }
}
