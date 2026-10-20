<script lang="ts">
  import { studio } from './studio.svelte'
  import { length } from './format'

  let canvas = $state<HTMLCanvasElement>()
  const SIZE = 240

  function loadImage(src: string) {
    const img = new Image()
    img.src = src
    return img.decode().then(() => img)
  }

  $effect(() => {
    const g = studio.grid
    const cell = studio.cell
    const src = studio.src
    const el = canvas
    const step = studio.current
    const raster = step === 'values' ? studio.values?.image : null
    const contour = step === 'contour' ? studio.contour : null
    const notan = step === 'light' ? studio.light : null
    const refOpacity = step === 'grid' ? 1 : studio.refOpacity
    if (!g || !cell || !src || !el) return

    let cancelled = false
    Promise.all([loadImage(src), raster ? loadImage(raster) : null]).then(([ref, top]) => {
      if (cancelled) return
      const ctx = el.getContext('2d')!
      const aspect = g.cell_height / g.cell_width
      el.width = SIZE * 2
      el.height = Math.round(SIZE * 2 * aspect)
      ctx.setTransform(1, 0, 0, 1, 0, 0)
      ctx.fillStyle = '#f4ecdc'
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

      // vector layers: zoom the working-size coordinates onto this one square
      const zoom = (width: number, height: number) => {
        const sx = el.width / (width / g.cols)
        const sy = el.height / (height / g.rows)
        ctx.setTransform(sx, 0, 0, sy, (-cell.col * width * sx) / g.cols, (-cell.row * height * sy) / g.rows)
        return sx
      }
      ctx.strokeStyle = ctx.fillStyle = '#24180f'
      ctx.lineCap = ctx.lineJoin = 'round'
      if (contour) {
        const s = zoom(contour.width, contour.height)
        for (const stroke of contour.strokes) {
          ctx.lineWidth = (stroke.weight * 2.2) / s
          ctx.stroke(new Path2D(stroke.d))
        }
      }
      if (notan) {
        zoom(notan.width, notan.height)
        ctx.globalAlpha = 0.8
        ctx.fill(new Path2D(notan.path), 'evenodd')
        ctx.globalAlpha = 1
      }
      ctx.setTransform(1, 0, 0, 1, 0, 0)

      // halfway marks, the same ones you'd sketch in faintly
      ctx.strokeStyle = 'rgba(142, 59, 34, 0.5)'
      ctx.setLineDash([6, 8])
      ctx.lineWidth = 1.5
      ctx.beginPath()
      ctx.moveTo(el.width / 2, 0)
      ctx.lineTo(el.width / 2, el.height)
      ctx.moveTo(0, el.height / 2)
      ctx.lineTo(el.width, el.height / 2)
      ctx.stroke()
      ctx.setLineDash([])
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
    margin-top: 0.8rem;
  }
  .name {
    margin: 0 0 0.4rem;
    font-family: var(--display);
    font-style: italic;
    font-size: 1.3rem;
  }
  canvas {
    display: block;
    max-width: 100%;
    height: auto;
    box-shadow: 0 10px 18px -12px rgb(40 22 8 / 0.6);
    transform: rotate(0.6deg);
  }
  .note,
  .empty {
    font-family: var(--script);
    color: var(--graphite);
    font-size: 1.35rem;
    line-height: 1.3;
  }
  .empty {
    color: var(--faint);
  }
</style>
