<script lang="ts">
  import { studio } from './studio.svelte'
  import { line, rect, type Stroke } from './sketch'

  const w = $derived(studio.size.w)
  const h = $derived(studio.size.h)
  const g = $derived(studio.grid)

  // stroke widths are in image pixels, so scale them with the image
  const unit = $derived(Math.max(w, h) / 700)

  const gridStrokes = $derived.by(() => {
    if (!g) return [] as Stroke[]
    const cw = w / g.cols
    const ch = h / g.rows
    const out: Stroke[] = []
    for (let i = 1; i < g.cols; i++) {
      out.push(...line(i * cw, 0, i * cw, h, { seed: i, width: unit }))
    }
    for (let j = 1; j < g.rows; j++) {
      out.push(...line(0, j * ch, w, j * ch, { seed: 100 + j, width: unit }))
    }
    out.push(...rect(0, 0, w, h, { seed: 7, width: unit * 1.4, roughness: 0.4 }))
    return out
  })

  const cellStrokes = $derived.by(() => {
    if (!g || !studio.cell) return [] as Stroke[]
    const cw = w / g.cols
    const ch = h / g.rows
    const { col, row } = studio.cell
    return rect(col * cw, row * ch, cw, ch, {
      seed: 3,
      width: unit * 2.2,
      roughness: 1.1,
      stroke: 'var(--sanguine)',
    })
  })

  const overlay = $derived(
    studio.step === 2 ? studio.contour : studio.step === 3 ? studio.values?.image : null,
  )
  const gridOn = $derived(studio.step >= 1 && studio.showGrid)
  // the reference fades back so the line drawing can show through
  const refOpacity = $derived(studio.step >= 2 ? studio.refOpacity : 1)

  function selectCell(e: MouseEvent) {
    if (!g || studio.step < 1) return
    const box = (e.currentTarget as SVGElement).getBoundingClientRect()
    const col = Math.floor(((e.clientX - box.left) / box.width) * g.cols)
    const row = Math.floor(((e.clientY - box.top) / box.height) * g.rows)
    const same = studio.cell?.col === col && studio.cell?.row === row
    studio.cell = same ? null : { col, row }
  }
</script>

<figure class="plate" style:aspect-ratio="{w} / {h}" style:width="min(100%, calc(76vh * {w / h}))">
  <img class="ref" src={studio.src} alt="your reference" style:opacity={refOpacity} />
  {#if overlay}
    <img class="overlay" src={overlay} alt="" />
  {/if}

  {#if gridOn && g}
    <!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
    <svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" onclick={selectCell}>
      <g class="grid">
        {#each gridStrokes as s}
          <path d={s.d} stroke={s.stroke} stroke-width={s.width} fill="none" />
        {/each}
      </g>
      {#each cellStrokes as s}
        <path d={s.d} stroke={s.stroke} stroke-width={s.width} fill="none" />
      {/each}
    </svg>

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
    background: var(--paper-light);
    box-shadow:
      0 0 0 1px var(--rule),
      0 18px 30px -24px rgb(60 45 25 / 0.45);
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
  svg {
    cursor: crosshair;
    overflow: visible;
  }
  .grid {
    color: var(--grid-line);
  }
  .labels {
    position: absolute;
    display: flex;
    font-family: var(--display);
    font-style: italic;
    font-size: 0.85rem;
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
    height: 1.4rem;
  }
  .side {
    top: 0;
    bottom: 0;
    right: 100%;
    width: 1.4rem;
    flex-direction: column;
  }
</style>
