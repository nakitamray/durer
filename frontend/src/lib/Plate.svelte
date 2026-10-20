<script lang="ts">
  import { studio } from './studio.svelte'
  import { line, rect, type Stroke } from './sketch'
  import { linesLayer, placementLayer, type Layer } from './layers'

  const w = $derived(studio.size.w)
  const h = $derived(studio.size.h)
  const g = $derived(studio.grid)
  const step = $derived(studio.current)

  const gridStrokes = $derived.by(() => {
    if (!g) return [] as Stroke[]
    const cw = w / g.cols
    const ch = h / g.rows
    const out: Stroke[] = []
    for (let i = 1; i < g.cols; i++) out.push(...line(i * cw, 0, i * cw, h, { seed: i }))
    for (let j = 1; j < g.rows; j++) out.push(...line(0, j * ch, w, j * ch, { seed: 100 + j }))
    out.push(...rect(0, 0, w, h, { seed: 7, width: 1.4, roughness: 0.4 }))
    return out
  })

  const cellStrokes = $derived.by(() => {
    if (!g || !studio.cell) return [] as Stroke[]
    const cw = w / g.cols
    const ch = h / g.rows
    const { col, row } = studio.cell
    return rect(col * cw, row * ch, cw, ch, { seed: 3, width: 2.4, roughness: 1.1 })
  })

  // block-in layers are measured at the api's working size
  const b = $derived(studio.blockin)
  const bScale = $derived(b ? w / b.width : 1)
  const none: Layer = { strokes: [], faint: [] }
  const layers = $derived.by(() => {
    if (!b) return { place: none, big: none, medium: none, small: none }
    return {
      place: placementLayer(b),
      big: linesLayer(b.big, 1.8, 10, 0.14),
      medium: linesLayer(b.medium, 1.3, 400, 0.08),
      small: linesLayer(b.small, 1, 900, 0.05),
    }
  })

  const light = $derived(step === 'light' ? studio.light : null)
  const turns = $derived(light ? linesLayer(light.turns, 1.4, 1500, 0.06) : none)

  const current = $derived.by((): Layer | null => {
    if (step === 'place' || step === 'big' || step === 'medium' || step === 'small') return layers[step]
    if (step === 'light') return turns
    return null
  })
  // the stages before, kept faintly underneath like a real block-in
  const ghost = $derived.by((): Layer | null => {
    if (!studio.ghost) return null
    if (step === 'big') return layers.place
    if (step === 'medium') return layers.big
    if (step === 'small') return layers.medium
    if (step === 'light' || step === 'contour') return layers.medium
    return null
  })

  const contour = $derived(step === 'contour' ? studio.contour : null)
  const values = $derived(step === 'values' ? studio.values : null)

  // where the placement marks land in the grid, written next to them
  const marks = $derived.by(() => {
    if (step !== 'place' || !b || !g) return []
    const [x0, y0, x1, y1] = b.placement.box
    const [cx, cy] = b.placement.center
    const at = (x: number, y: number) => {
      const c = Math.min(g.cols - 1, Math.floor((x / b.width) * g.cols))
      const r = Math.min(g.rows - 1, Math.floor((y / b.height) * g.rows))
      return `${g.col_labels[c]}${g.row_labels[r]}`
    }
    const pct = (x: number, y: number) => ({ left: (x / b.width) * 100, top: (y / b.height) * 100 })
    return [
      { text: `top ${at(cx, y0)}`, ...pct(cx, y0), cls: 'above' },
      { text: `bottom ${at(cx, y1)}`, ...pct(cx, y1), cls: 'below' },
      { text: `left ${at(x0, cy)}`, ...pct(x0, cy), cls: 'leftof' },
      { text: `right ${at(x1, cy)}`, ...pct(x1, cy), cls: 'rightof' },
    ]
  })

  const gridOn = $derived(step !== 'setup' && studio.showGrid)
  const refOpacity = $derived(step === 'setup' || step === 'grid' ? 1 : studio.refOpacity)

  function selectCell(e: MouseEvent) {
    if (!g || step === 'setup') return
    const box = (e.currentTarget as SVGElement).getBoundingClientRect()
    const col = Math.floor(((e.clientX - box.left) / box.width) * g.cols)
    const row = Math.floor(((e.clientY - box.top) / box.height) * g.rows)
    const same = studio.cell?.col === col && studio.cell?.row === row
    studio.cell = same ? null : { col, row }
  }
</script>

{#snippet strokes(list: Stroke[], cls = '')}
  {#each list as s}
    <path
      class={cls}
      d={s.d}
      stroke-width={s.width}
      fill="none"
      vector-effect="non-scaling-stroke"
    />
  {/each}
{/snippet}

<figure class="plate" style:aspect-ratio="{w} / {h}" style:width="min(100%, calc((100vh - 5rem) * {w / h}))">
  <span class="tape tr" aria-hidden="true"></span>
  <span class="tape bl" aria-hidden="true"></span>

  <img class="ref" src={studio.src} alt="your reference" style:opacity={refOpacity} />
  {#if values}
    <img class="overlay" src={values.image} alt="" />
  {/if}

  <!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
  <svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" onclick={selectCell}>
    <defs>
      <pattern id="hatch" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(-40)">
        <line x1="0" y1="0" x2="0" y2="4" stroke="var(--ink)" stroke-width="1.1" />
      </pattern>
    </defs>

    {#if light}
      <g transform="scale({w / light.width})">
        <path
          class="notan"
          class:solid={!studio.hatched}
          d={light.path}
          fill-rule="evenodd"
          fill={studio.hatched ? 'url(#hatch)' : 'var(--ink)'}
        />
      </g>
    {/if}

    {#if b}
      <g transform="scale({bScale})" class="ink">
        {#if ghost}
          <g class="ghost">
            {@render strokes(ghost.strokes)}
            {@render strokes(ghost.faint)}
          </g>
        {/if}
        {#if current}
          {@render strokes(current.faint, 'faint')}
          {@render strokes(current.strokes)}
        {/if}
      </g>
    {/if}

    {#if contour}
      <g transform="scale({w / contour.width})" class="ink contour">
        {#each contour.strokes as s}
          <path d={s.d} stroke-width={s.weight * 1.15} fill="none" vector-effect="non-scaling-stroke" />
        {/each}
      </g>
    {/if}

    {#if gridOn && g}
      <g class="grid">{@render strokes(gridStrokes)}</g>
      <g class="cell">{@render strokes(cellStrokes)}</g>
    {/if}
  </svg>

  {#each marks as m}
    <span class="mark {m.cls}" style:left="{m.left}%" style:top="{m.top}%">{m.text}</span>
  {/each}

  {#if gridOn && g}
    <div class="labels top">
      {#each g.col_labels as label}<span>{label}</span>{/each}
    </div>
    <div class="labels side">
      {#each g.row_labels as label}<span>{label}</span>{/each}
    </div>
  {/if}
</figure>

<style>
  .plate {
    position: relative;
    margin: 0 auto;
    background: var(--sheet);
    box-shadow:
      0 1px 0 rgb(255 255 255 / 0.15) inset,
      0 22px 40px -22px rgb(40 22 8 / 0.65),
      0 2px 6px rgb(40 22 8 / 0.25);
    transform: rotate(-0.4deg);
  }
  img,
  svg {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    display: block;
  }
  img {
    object-fit: fill;
    transition: opacity 0.25s;
  }
  .overlay {
    mix-blend-mode: multiply;
  }
  svg {
    cursor: crosshair;
    overflow: visible;
  }
  svg path {
    stroke: currentColor;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
  .ink {
    color: var(--ink);
  }
  .ghost {
    opacity: 0.3;
  }
  .faint {
    opacity: 0.45;
  }
  .newest {
    color: var(--sanguine);
  }
  .notan {
    stroke: none;
  }
  .mark {
    position: absolute;
    z-index: 3;
    font-family: var(--script);
    font-size: 1.4rem;
    white-space: nowrap;
    color: var(--sanguine);
    text-shadow:
      0 0 3px var(--sheet),
      0 0 6px var(--sheet);
    pointer-events: none;
  }
  .mark.above {
    transform: translate(-50%, -125%);
  }
  .mark.below {
    transform: translate(-50%, 15%);
  }
  .mark.leftof {
    transform: translate(-110%, -50%);
  }
  .mark.rightof {
    transform: translate(10%, -50%);
  }
  .notan.solid {
    opacity: 0.82;
  }
  .grid {
    color: var(--grid-line);
  }
  .cell {
    color: var(--sanguine);
  }
  .tape {
    position: absolute;
    z-index: 2;
    width: 5.5rem;
    height: 1.6rem;
    background: rgb(232 222 196 / 0.72);
    box-shadow: 0 1px 2px rgb(40 22 8 / 0.2);
    pointer-events: none;
  }
  .tape.tr {
    top: -0.5rem;
    right: -1.8rem;
    transform: rotate(36deg);
  }
  .tape.bl {
    bottom: -0.4rem;
    left: -1.8rem;
    transform: rotate(38deg);
  }
  .labels {
    position: absolute;
    display: flex;
    font-family: var(--display);
    font-style: italic;
    font-size: 0.9rem;
    color: var(--graphite);
    pointer-events: none;
  }
  .labels span {
    flex: 1;
    display: grid;
    place-items: center;
  }
  .top {
    left: 0;
    right: 0;
    bottom: 100%;
    height: 1.5rem;
  }
  .side {
    top: 0;
    bottom: 0;
    right: 100%;
    width: 1.5rem;
    flex-direction: column;
  }
</style>
