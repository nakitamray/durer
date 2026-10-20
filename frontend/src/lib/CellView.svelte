<script lang="ts">
  import { studio } from './studio.svelte'
  import { length } from './format'

  let canvas = $state<HTMLCanvasElement>()
  const SIZE = 220

  function loadImage(src: string) {
    const img = new Image()
    img.src = src
    return img.decode().then(() => img)
  }

  $effect(() => {
    const g = studio.grid
    const cell = studio.cell
    const src = studio.src
    const overlay =
      studio.current === 'contour'
        ? studio.contour
        : studio.current === 'values'
          ? studio.values?.image
          : null
    const refOpacity = studio.step >= 2 ? studio.refOpacity : 1
    const el = canvas
    if (!g || !cell || !src || !el) return

    let cancelled = false
    Promise.all([loadImage(src), overlay ? loadImage(overlay) : null]).then(([ref, top]) => {
      if (cancelled) return
      const ctx = el.getContext('2d')!
      const aspect = g.cell_height / g.cell_width
      el.width = SIZE * 2
      el.height = Math.round(SIZE * 2 * aspect)

      ctx.fillStyle = '#f7f2e8'
      ctx.fillRect(0, 0, el.width, el.height)

      const crop = (img: HTMLImageElement) => {
        const cw = img.naturalWidth / g.cols
        const ch = img.naturalHeight / g.rows
        ctx.drawImage(img, cell.col * cw, cell.row * ch, cw, ch, 0, 0, el.width, el.height)
      }
      ctx.globalAlpha = refOpacity
      crop(ref)
      ctx.globalAlpha = 1
      if (top) crop(top)

      // halfway marks, the same ones you'd sketch in faintly
      ctx.strokeStyle = 'rgba(164, 85, 58, 0.45)'
      ctx.setLineDash([6, 8])
      ctx.lineWidth = 1.5
      ctx.beginPath()
      ctx.moveTo(el.width / 2, 0)
      ctx.lineTo(el.width / 2, el.height)
      ctx.moveTo(0, el.height / 2)
      ctx.lineTo(el.width, el.height / 2)
      ctx.stroke()
    })

    return () => {
      cancelled = true
    }
  })
</script>

{#if studio.cell && studio.grid}
  {@const g = studio.grid}
  <div class="cell">
    <p class="name">
      Square {g.col_labels[studio.cell.col]}{g.row_labels[studio.cell.row]}
    </p>
    <canvas bind:this={canvas} style:width="{SIZE}px"></canvas>
    <p class="note">
      {length(g.cell_width, g.unit)} wide, {length(g.cell_height, g.unit)} tall on your paper
    </p>
  </div>
{:else if studio.grid}
  <p class="empty">click any square to study it up close</p>
{/if}

<style>
  .cell {
    margin-top: 0.5rem;
  }
  .name {
    margin: 0 0 0.4rem;
    font-family: var(--display);
    font-style: italic;
    font-size: 1.25rem;
  }
  canvas {
    display: block;
    max-width: 100%;
    height: auto;
    box-shadow: 0 0 0 1px var(--rule);
  }
  .note,
  .empty {
    font-family: var(--hand);
    color: var(--graphite);
    font-size: 1.05rem;
    line-height: 1.5;
  }
  .empty {
    color: var(--faint);
  }
</style>
