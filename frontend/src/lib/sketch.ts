import rough from 'roughjs'

const gen = rough.generator()

export interface Stroke {
  d: string
  stroke: string
  width: number
}

type Opts = { roughness?: number; bowing?: number; seed?: number; stroke?: string; width?: number }

function toStrokes(drawable: ReturnType<typeof gen.line>, color: string, width: number): Stroke[] {
  return gen.toPaths(drawable).map((p) => ({ d: p.d, stroke: color, width }))
}

// slightly wobbly lines so nothing looks ruled by a machine
export function line(x1: number, y1: number, x2: number, y2: number, o: Opts = {}): Stroke[] {
  const d = gen.line(x1, y1, x2, y2, {
    roughness: o.roughness ?? 0.6,
    bowing: o.bowing ?? 0.8,
    seed: o.seed ?? 1,
    disableMultiStroke: true,
  })
  return toStrokes(d, o.stroke ?? 'currentColor', o.width ?? 1)
}

export function rect(x: number, y: number, w: number, h: number, o: Opts = {}): Stroke[] {
  const d = gen.rectangle(x, y, w, h, {
    roughness: o.roughness ?? 0.8,
    bowing: o.bowing ?? 1,
    seed: o.seed ?? 1,
  })
  return toStrokes(d, o.stroke ?? 'currentColor', o.width ?? 1)
}

export function path(svgPath: string, o: Opts = {}): Stroke[] {
  const d = gen.path(svgPath, {
    roughness: o.roughness ?? 0.7,
    bowing: o.bowing ?? 1,
    seed: o.seed ?? 1,
  })
  return toStrokes(d, o.stroke ?? 'currentColor', o.width ?? 1)
}
