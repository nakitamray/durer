<script lang="ts">
  import CellView from './CellView.svelte'
  import ToneKey from './ToneKey.svelte'
  import { length, percent } from './format'
  import { PAPERS } from './papers'
  import { describe } from './shapes'
  import { studio } from './studio.svelte'

  const g = $derived(studio.grid)
  const b = $derived(studio.blockin)
  const step = $derived(studio.current)
  const paperIndex = $derived(PAPERS.findIndex((p) => p.label === studio.paper.label))

  const DETAIL = ['very loose', 'loose', 'balanced', 'detailed', 'every line']
  const SIMPLICITY = ['lots of pieces', 'more pieces', 'balanced', 'fewer pieces', 'just the masses']
  const BIAS = ['mostly light', 'lighter', 'balanced', 'darker', 'mostly shadow']

  // where the subject lands on the paper and in the grid
  const where = $derived.by(() => {
    if (!g || !b) return null
    const [x0, y0, x1, y1] = b.placement.box
    const fx = (v: number) => v / b.width
    const fy = (v: number) => v / b.height
    const col = (v: number) => g.col_labels[Math.min(g.cols - 1, Math.floor(fx(v) * g.cols))]
    const row = (v: number) => g.row_labels[Math.min(g.rows - 1, Math.floor(fy(v) * g.rows))]
    const lean = b.placement.lean
    return {
      width: length((fx(x1) - fx(x0)) * g.drawing_width, g.unit),
      height: length((fy(y1) - fy(y0)) * g.drawing_height, g.unit),
      top: `${col((x0 + x1) / 2)}${row(y0)}`,
      bottom: `${col((x0 + x1) / 2)}${row(y1)}`,
      left: `${col(x0)}${row((y0 + y1) / 2)}`,
      right: `${col(x1)}${row((y0 + y1) / 2)}`,
      lean:
        Math.abs(lean) < 4
          ? 'stands straight up'
          : `tips ${Math.round(Math.abs(lean))}° with the top to the ${lean > 0 ? 'left' : 'right'}`,
    }
  })
  const bigCount = $derived(b ? b.big.reduce((n, p) => n + p.length, 0) : 0)
</script>

{#snippet referenceControls()}
  <label class="field">
    <span>Photo underneath</span>
    <input type="range" min="0" max="1" step="0.05" bind:value={studio.refOpacity} />
  </label>
  <div class="checks">
    <label><input type="checkbox" bind:checked={studio.showGrid} /> grid</label>
    {#if step !== 'place' && step !== 'values'}
      <label><input type="checkbox" bind:checked={studio.ghost} /> last stage</label>
    {/if}
  </div>
{/snippet}

<aside>
  {#if step === 'setup'}
    <h2>Your paper</h2>
    <label class="field">
      <span>Size</span>
      <select value={paperIndex} onchange={(e) => studio.setPaper(PAPERS[+e.currentTarget.value])}>
        {#each PAPERS as p, i}
          <option value={i}>{p.label}</option>
        {/each}
      </select>
    </label>
    <button class="link" onclick={() => studio.rotatePaper()}>
      turn it {studio.paper.width > studio.paper.height ? 'upright' : 'sideways'}
    </button>
    {#if g}
      <p class="note">
        the drawing will be {length(g.drawing_width, g.unit)} × {length(g.drawing_height, g.unit)}
      </p>
    {/if}
    <p class="tip">
      Pick the sheet you're actually going to draw on. Every measurement after this is in real
      inches or centimetres on that paper.
    </p>
    <button class="next" onclick={() => (studio.step = 1)}>On to the grid →</button>
  {:else if step === 'grid'}
    <h2>The grid</h2>
    <label class="field">
      <span>Squares across <b>{studio.cols}</b></span>
      <input type="range" min="2" max="20" bind:value={studio.cols} />
    </label>
    {#if g}
      <p class="note big">
        each square {length(g.cell_width, g.unit)}<br />
        {g.cols} across · {g.rows} down
      </p>
    {/if}
    <p class="tip">
      Rule the same grid on your paper with a 2H, pressing lightly so it erases later. Then copy one
      square at a time and only look at what's inside it.
    </p>
    <button class="link" onclick={() => studio.downloadPdf()}>print this grid (pdf)</button>
    <CellView />
  {:else if step === 'place'}
    <h2>Placement</h2>
    {#if where}
      <p class="note big">
        {where.width} wide<br />{where.height} tall
      </p>
      <ul class="facts">
        <li>top edge in <b>{where.top}</b>, bottom in <b>{where.bottom}</b></li>
        <li>left edge in <b>{where.left}</b>, right in <b>{where.right}</b></li>
        <li>it {where.lean}</li>
      </ul>
    {/if}
    <p class="tip">
      Before anything else, make four light marks: the highest, lowest, leftmost and rightmost
      points. Then the line it leans along. If these are right, the drawing fits the page.
    </p>
    {@render referenceControls()}
  {:else if step === 'big'}
    <h2>Big shapes</h2>
    <div class="toggle" role="radiogroup" aria-label="how to show the big shapes">
      <button class:on={!studio.solids} onclick={() => (studio.solids = false)}>straight lines</button>
      <button class:on={studio.solids} onclick={() => (studio.solids = true)}>simple solids</button>
    </div>
    {#if studio.solids}
      <label class="field">
        <span>Simplicity <i>{SIMPLICITY[studio.simplicity - 1]}</i></span>
        <input type="range" min="1" max="5" bind:value={studio.simplicity} />
      </label>
      {#if studio.shapes}
        <ol class="shapes">
          {#each studio.shapes.shapes.slice(0, 8) as s, i}
            <li><span class="n">{i + 1}</span>{describe(s)}<span class="share">{percent(s.share)}</span></li>
          {/each}
        </ol>
      {/if}
      <p class="tip">The same subject as a few solids. Biggest first.</p>
    {:else}
      {#if b}<p class="note">the whole thing in {bigCount} straight lines</p>{/if}
      <p class="tip">
        Wrap the subject in as few straight lines as you can, like a box that fits it. Let the lines
        run long past the corners. Don't curve anything yet.
      </p>
    {/if}
    {@render referenceControls()}
  {:else if step === 'medium'}
    <h2>Medium shapes</h2>
    <p class="tip">
      Break each big line into two or three shorter ones, still straight. Add the shapes of the main
      shadows inside, as flat angled planes. Check every angle against the grid.
    </p>
    {@render referenceControls()}
  {:else if step === 'notan'}
    <h2>Notan</h2>
    <label class="field">
      <span>Split <i>{BIAS[studio.bias - 1]}</i></span>
      <input type="range" min="1" max="5" bind:value={studio.bias} />
    </label>
    {#if studio.notan}
      <p class="note">{percent(studio.notan.shadow)} of the picture is in shadow</p>
    {/if}
    <div class="toggle">
      <button class:on={studio.hatched} onclick={() => (studio.hatched = true)}>hatched</button>
      <button class:on={!studio.hatched} onclick={() => (studio.hatched = false)}>solid</button>
    </div>
    <p class="tip">
      Only two values: light and shadow. Fill every shadow shape with one flat even tone. If the
      picture still reads at this stage, the rest is polish.
    </p>
    {@render referenceControls()}
    <CellView />
  {:else if step === 'contour'}
    <h2>The real lines</h2>
    <label class="field">
      <span>Detail <i>{DETAIL[studio.detail - 1]}</i></span>
      <input type="range" min="1" max="5" bind:value={studio.detail} />
    </label>
    {#if studio.contour}
      <p class="note">{studio.contour.strokes.length} strokes</p>
    {/if}
    <p class="tip">
      Now curve the straight lines into the real edges, using the block-in underneath as a guide.
      Vary the pressure: heavier where an edge turns into shadow, lighter where it catches the light.
    </p>
    {@render referenceControls()}
    <CellView />
  {:else}
    <h2>Values</h2>
    <div class="toggle" role="radiogroup" aria-label="number of tones">
      {#each [3, 4, 5] as n}
        <button class:on={studio.levels === n} onclick={() => (studio.levels = n)}>{n} tones</button>
      {/each}
    </div>
    {#if studio.values}
      <ToneKey tones={studio.values.tones} />
    {/if}
    <p class="tip">
      Squint at the picture. Leave the paper areas alone, lay in your lightest pencil everywhere
      else, then build up darker grades one at a time. Save the darkest for last.
    </p>
    <label class="field">
      <span>Photo underneath</span>
      <input type="range" min="0" max="1" step="0.05" bind:value={studio.refOpacity} />
    </label>
    <div class="checks">
      <label><input type="checkbox" bind:checked={studio.showGrid} /> grid</label>
    </div>
    <CellView />
  {/if}

  {#if studio.error}
    <p class="error">{studio.error}</p>
  {/if}
</aside>

<style>
  aside {
    font-size: 0.98rem;
  }
  h2 {
    margin: 0 0 1rem;
    font-family: var(--display);
    font-weight: 500;
    font-style: italic;
    font-size: 2rem;
  }
  .field {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    margin-bottom: 1rem;
  }
  .field span {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    color: var(--graphite);
  }
  .field b {
    font-family: var(--display);
    font-size: 1.2rem;
    font-weight: 500;
    color: var(--ink);
  }
  .field i {
    font-family: var(--hand);
    -webkit-text-stroke: 0.45px currentColor;
    font-style: normal;
    font-size: 1.6rem;
    color: var(--sanguine);
  }
  .checks {
    display: flex;
    gap: 1.2rem;
    color: var(--graphite);
  }
  .checks label {
    display: flex;
    align-items: center;
    gap: 0.35rem;
  }
  .note {
    font-family: var(--hand);
    -webkit-text-stroke: 0.45px currentColor;
    font-size: 1.85rem;
    line-height: 1.25;
    color: var(--sanguine);
    transform: rotate(-1.5deg);
    transform-origin: left;
  }
  .note.big {
    font-size: 2.3rem;
  }
  .facts {
    margin: 0 0 1rem;
    padding-left: 1rem;
    color: var(--graphite);
    line-height: 1.6;
  }
  .facts b {
    font-family: var(--display);
    font-weight: 500;
    color: var(--ink);
  }
  .tip {
    color: var(--graphite);
    line-height: 1.55;
    padding-left: 0.8rem;
    border-left: 1px solid var(--rule);
  }
  .link {
    padding: 0;
    border: 0;
    background: none;
    color: var(--ink);
    font: inherit;
    font-style: italic;
    text-decoration: underline;
    text-decoration-color: var(--faint);
    text-underline-offset: 3px;
    cursor: pointer;
  }
  .link:hover {
    text-decoration-color: var(--sanguine);
  }
  .next {
    margin-top: 0.5rem;
    padding: 0.5rem 1.1rem;
    border: 1px solid var(--ink);
    border-radius: 2px;
    background: transparent;
    color: var(--ink);
    font-family: var(--display);
    font-style: italic;
    font-size: 1.15rem;
    cursor: pointer;
  }
  .next:hover {
    background: var(--ink);
    color: var(--sheet);
  }
  .toggle {
    display: flex;
    gap: 0.4rem;
    margin-bottom: 1rem;
  }
  .toggle button {
    flex: 1;
    padding: 0.35rem 0;
    border: 1px solid var(--rule);
    border-radius: 2px;
    background: transparent;
    color: var(--graphite);
    font: inherit;
    cursor: pointer;
  }
  .toggle button.on {
    border-color: var(--ink);
    color: var(--ink);
    background: rgb(255 255 255 / 0.12);
  }
  .shapes {
    list-style: none;
    margin: 0 0 1rem;
    padding: 0;
  }
  .shapes li {
    display: grid;
    grid-template-columns: 1.8rem 1fr auto;
    padding: 0.25rem 0;
    border-bottom: 1px solid var(--rule);
  }
  .shapes .n {
    font-family: var(--hand);
    -webkit-text-stroke: 0.45px currentColor;
    font-size: 1.2rem;
    color: var(--sanguine);
  }
  .shapes .share {
    color: var(--graphite);
    font-size: 0.85rem;
  }
  .error {
    color: var(--sanguine);
    font-style: italic;
  }
</style>
