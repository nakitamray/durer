import rough from 'roughjs'

const gen = rough.generator()

export interface Mark {
  d: string
  stroke: string
  fill: string
  width: number
}

type Drawable = ReturnType<typeof gen.line>

const INK = 'var(--ink)'

function marks(...drawables: Drawable[]): Mark[] {
  return drawables.flatMap((dr) =>
    gen.toPaths(dr).map((p) => ({ d: p.d, stroke: p.stroke, fill: p.fill ?? 'none', width: p.strokeWidth })),
  )
}

const pen = (seed: number, extra: object = {}) => ({
  stroke: INK,
  strokeWidth: 1.1,
  roughness: 1.1,
  seed,
  ...extra,
})

const hatch = (seed: number, gap = 4, extra: object = {}) =>
  pen(seed, {
    fill: INK,
    fillStyle: 'hachure',
    hachureAngle: -41,
    hachureGap: gap,
    fillWeight: 0.6,
    ...extra,
  })

// a lit sphere with its core shadow and cast shadow, the first thing anyone draws
export function sphere(): Mark[] {
  return marks(
    gen.ellipse(150, 152, 130, 26, hatch(4, 3.2, { fillStyle: 'cross-hatch', stroke: 'none' })),
    gen.path('M92 22 A56 56 0 0 1 92 134 A38 56 0 0 0 92 22 Z', hatch(3, 3.6, { stroke: 'none' })),
    gen.circle(92, 78, 112, pen(1, { roughness: 1.4 })),
    gen.circle(92, 78, 114, pen(2, { strokeWidth: 0.5, roughness: 2 })),
    gen.line(8, 6, 38, 30, pen(5)),
    gen.line(38, 30, 26, 29, pen(6)),
    gen.line(38, 30, 36, 18, pen(7)),
  )
}

// two point perspective, construction lines running off toward the vanishing points
export function cube(): Mark[] {
  const faint = (seed: number) => pen(seed, { strokeWidth: 0.5, roughness: 1.6 })
  return marks(
    gen.line(-10, 90, 270, 52, faint(20)),
    gen.line(-10, 30, 120, 74, faint(21)),
    gen.line(250, 22, 130, 74, faint(22)),
    gen.line(0, 158, 130, 172, faint(23)),
    gen.line(262, 140, 130, 172, faint(24)),
    gen.polygon(
      [
        [130, 82],
        [214, 64],
        [214, 140],
        [130, 172],
      ],
      hatch(25, 4.5),
    ),
    gen.polygon(
      [
        [130, 82],
        [56, 66],
        [56, 150],
        [130, 172],
      ],
      pen(26),
    ),
    gen.polygon(
      [
        [56, 66],
        [138, 50],
        [214, 64],
        [130, 82],
      ],
      pen(27),
    ),
  )
}

// a five step value scale, from bare paper to the darkest you can press
export function valueScale(): Mark[] {
  const gaps = [0, 7, 4.5, 3, 2]
  return marks(
    ...gaps.map((gap, i) =>
      gen.rectangle(
        4 + i * 44,
        6,
        40,
        34,
        gap
          ? hatch(40 + i, gap, { fillStyle: i === 4 ? 'cross-hatch' : 'hachure', roughness: 0.9 })
          : pen(40 + i, { roughness: 0.9 }),
      ),
    ),
  )
}

// a fineliner, lying horizontally; it gets rotated in css
export function fineliner(): Mark[] {
  const solid = (seed: number, fill: string, extra: object = {}) =>
    pen(seed, { fill, fillStyle: 'solid', roughness: 0.6, ...extra })
  return marks(
    // tip
    gen.line(4, 35, 22, 35, pen(60, { strokeWidth: 1.8, roughness: 0.4 })),
    gen.polygon(
      [
        [22, 31],
        [44, 26],
        [44, 44],
        [22, 39],
      ],
      solid(61, '#9a9790'),
    ),
    // grip
    gen.rectangle(44, 22, 70, 26, solid(62, '#3b3a38')),
    ...[56, 66, 76, 86, 96, 106].map((x, i) => gen.line(x, 23, x, 47, pen(63 + i, { stroke: '#77746e', strokeWidth: 0.8 }))),
    // barrel
    gen.rectangle(114, 20, 270, 30, solid(70, '#ece4d4')),
    gen.line(118, 44, 380, 44, pen(71, { strokeWidth: 0.6 })),
    gen.rectangle(118, 41, 262, 7, hatch(72, 2.4, { stroke: 'none', hachureAngle: -60 })),
    // cap
    gen.rectangle(384, 18, 120, 34, solid(73, '#24201c')),
    gen.polygon(
      [
        [410, 18],
        [470, 18],
        [474, 6],
        [416, 6],
      ],
      solid(74, '#24201c'),
    ),
    gen.line(392, 26, 498, 26, pen(75, { stroke: '#6d6862', strokeWidth: 0.8 })),
  )
}

// a used white eraser half out of its paper sleeve
export function eraser(): Mark[] {
  const solid = (seed: number, fill: string, extra: object = {}) =>
    pen(seed, { fill, fillStyle: 'solid', roughness: 0.8, ...extra })
  return marks(
    gen.path('M14 40 Q10 26 24 22 L190 22 L190 82 L26 82 Q12 80 14 40 Z', solid(80, '#f2ede3')),
    gen.path('M14 40 Q10 26 24 22 L44 22 Q32 30 34 52 Q34 72 26 82 Q12 80 14 40 Z', hatch(81, 3, { stroke: 'none' })),
    gen.rectangle(92, 16, 108, 72, solid(82, '#6f8797')),
    gen.rectangle(92, 16, 108, 72, hatch(83, 5, { hachureAngle: 50, stroke: 'none' })),
    gen.line(104, 30, 186, 30, pen(84, { stroke: '#e9e2d3', strokeWidth: 1.6 })),
    gen.line(104, 40, 160, 40, pen(85, { stroke: '#e9e2d3', strokeWidth: 0.9 })),
    // crumbs
    ...[
      [-20, 96],
      [-6, 110],
      [8, 100],
      [-34, 112],
      [22, 116],
    ].map(([x, y], i) => gen.ellipse(x, y, 7 + (i % 3) * 2, 4 + (i % 2) * 2, solid(86 + i, '#e8e1d3', { strokeWidth: 0.7 }))),
  )
}

// long faint lines across the page, like the leftovers of a construction
export function scaffold(w: number, h: number): Mark[] {
  const faint = (seed: number) => pen(seed, { strokeWidth: 0.6, roughness: 2, bowing: 3 })
  return marks(
    gen.line(w * 0.02, h * 0.9, w * 0.36, -h * 0.05, faint(90)),
    gen.line(w * 0.7, h * 1.02, w * 1.02, h * 0.34, faint(91)),
    gen.line(-w * 0.02, h * 0.24, w * 0.22, h * 0.31, faint(92)),
    gen.line(w * 0.84, -h * 0.02, w * 0.97, h * 0.2, faint(93)),
    gen.line(w * 0.3, h * 1.02, w * 0.55, h * 0.93, faint(94)),
  )
}

// Dürer's drawing frame: a window strung with a grid of threads, and the
// sight post you'd keep your eye at
export function durerFrame(): Mark[] {
  const faint = (seed: number) => pen(seed, { strokeWidth: 0.6, roughness: 1 })
  const threads = [1, 2, 3].flatMap((i) => [
    gen.line(60 + i * 30, 22, 60 + i * 30, 142, faint(100 + i)),
    gen.line(60, 22 + i * 30, 180, 22 + i * 30, faint(110 + i)),
  ])
  return marks(
    gen.rectangle(56, 18, 128, 128, pen(120, { strokeWidth: 1.6 })),
    gen.rectangle(52, 14, 136, 136, pen(121, { strokeWidth: 0.6, roughness: 1.6 })),
    ...threads,
    // stand
    gen.line(120, 150, 120, 190, pen(122)),
    gen.line(92, 192, 148, 192, pen(123)),
    // sight post and the eye's line through the frame
    gen.line(14, 112, 14, 192, pen(124)),
    gen.circle(14, 106, 9, pen(125)),
    gen.line(16, 104, 226, 60, pen(126, { strokeWidth: 0.5, roughness: 2, strokeLineDash: [4, 5] })),
    // the table it all sits on
    gen.line(-10, 194, 250, 194, hatch(127, 3, { strokeWidth: 0.8 })),
  )
}

// a chess king worked out as stacked ellipses around a centre line, the
// way you'd study any turned object before drawing it
export function kingStudy(): Mark[] {
  const cx = 160
  const tilt = 0.26 // how open the ellipses are, from just above eye level
  // the profile, top to bottom: height and radius at each section
  const sections: [number, number][] = [
    [78, 26],
    [122, 16],
    [130, 36],
    [142, 34],
    [156, 20],
    [280, 30],
    [292, 46],
    [304, 44],
    [318, 40],
    [404, 84],
    [414, 96],
    [436, 96],
  ]
  const faint = (seed: number) => pen(seed, { strokeWidth: 0.5, roughness: 1.4 })
  const out: Drawable[] = []
  let seed = 300

  // centre line and the guide lines running out past the silhouette
  out.push(gen.line(cx, 0, cx, 470, faint(seed++)))
  for (const [y, r] of sections.filter((_, i) => [0, 2, 6, 9, 11].includes(i))) {
    out.push(gen.line(cx - r - 50, y, cx + r + 60, y, faint(seed++)))
  }
  // a measuring line down the side with ticks at each key height
  out.push(gen.line(24, 40, 24, 440, pen(seed++, { strokeWidth: 0.7 })))
  for (const [y] of sections.filter((_, i) => i % 2 === 0)) {
    out.push(gen.line(18, y, 30, y, pen(seed++, { strokeWidth: 0.7 })))
  }

  // the cross on top
  out.push(gen.rectangle(cx - 5, 22, 10, 44, pen(seed++)))
  out.push(gen.rectangle(cx - 18, 34, 36, 10, pen(seed++)))

  // an ellipse at every section, some boxed in with their diagonals
  sections.forEach(([y, r], i) => {
    const h = r * 2 * tilt
    out.push(gen.ellipse(cx, y, r * 2, h, pen(seed++, { roughness: 1.2 })))
    if (i === 2 || i === 6 || i === 10) {
      out.push(gen.rectangle(cx - r, y - h / 2, r * 2, h, faint(seed++)))
      out.push(gen.line(cx - r, y - h / 2, cx + r, y + h / 2, faint(seed++)))
      out.push(gen.line(cx - r, y + h / 2, cx + r, y - h / 2, faint(seed++)))
    }
  })

  // silhouette: join the ends of each section to the next
  for (let i = 0; i < sections.length - 1; i++) {
    const [y1, r1] = sections[i]
    const [y2, r2] = sections[i + 1]
    for (const side of [-1, 1]) {
      if (i === 8) {
        // the body flares out in a curve
        const x1 = cx + side * r1
        const x2 = cx + side * r2
        out.push(gen.curve([[x1, y1], [cx + side * (r1 + 8), y1 + 50], [x2, y2]], pen(seed++, { strokeWidth: 1.3 })))
      } else {
        out.push(gen.line(cx + side * r1, y1, cx + side * r2, y2, pen(seed++, { strokeWidth: 1.3 })))
      }
    }
  }

  // the shadow side of the body and the base, hatched
  out.push(
    gen.polygon(
      [
        [cx + 12, 318],
        [cx + 40, 318],
        [cx + 50, 368],
        [cx + 84, 404],
        [cx + 96, 414],
        [cx + 96, 436],
        [cx + 40, 445],
        [cx + 30, 404],
      ],
      hatch(seed++, 3.4, { stroke: 'none' }),
    ),
  )
  out.push(gen.polygon([[cx + 8, 160], [cx + 20, 156], [cx + 30, 280], [cx + 14, 284]], hatch(seed++, 3, { stroke: 'none' })))
  return marks(...out)
}
