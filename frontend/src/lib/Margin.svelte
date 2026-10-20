<script lang="ts">
  import CellView from './CellView.svelte'
  import ToneKey from './ToneKey.svelte'
  import { length } from './format'
  import { PAPERS } from './papers'
  import { studio } from './studio.svelte'

  const g = $derived(studio.grid)
  const paperIndex = $derived(PAPERS.findIndex((p) => p.label === studio.paper.label))
  const DETAIL = ['very loose', 'loose', 'balanced', 'detailed', 'every line']
</script>

<aside>
  {#if studio.step === 0}
    <h2>Your paper</h2>
    <label class="field">
      <span>Size</span>
      <select
        value={paperIndex}
        onchange={(e) => studio.setPaper(PAPERS[+e.currentTarget.value])}
      >
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
        the drawing will be {length(g.drawing_width, g.unit)} × {length(g.drawing_height, g.unit)},
        centered on the sheet
      </p>
    {/if}

    <p class="tip">
      Pick the sheet you're actually going to draw on. Every measurement after this is in real
      inches or centimetres on that paper.
    </p>
    <button class="next" onclick={() => (studio.step = 1)}>On to the grid →</button>
  {:else if studio.step === 1}
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
      Rule the same grid on your paper with a 2H, pressing lightly so it erases later. Then copy
      one square at a time and only look at what's inside it.
    </p>
    <button class="link" onclick={() => studio.downloadPdf()}>print this grid (pdf)</button>
    <CellView />
  {:else if studio.step === 2}
    <h2>Main lines</h2>
    <label class="field">
      <span>Detail <i>{DETAIL[studio.detail - 1]}</i></span>
      <input type="range" min="1" max="5" bind:value={studio.detail} />
    </label>
    <label class="field">
      <span>Photo underneath</span>
      <input type="range" min="0" max="1" step="0.05" bind:value={studio.refOpacity} />
    </label>
    <label class="check">
      <input type="checkbox" bind:checked={studio.showGrid} /> show grid
    </label>
    <p class="tip">
      Start loose. Get the big edges into every square before any detail. Where a line crosses a
      grid line, mark that spot first and connect the dots.
    </p>
    <CellView />
  {:else}
    <h2>Values</h2>
    <div class="levels" role="radiogroup" aria-label="number of tones">
      {#each [3, 4, 5] as n}
        <button class:on={studio.levels === n} onclick={() => (studio.levels = n)}>
          {n} tones
        </button>
      {/each}
    </div>
    {#if studio.values}
      <ToneKey tones={studio.values.tones} />
    {/if}
    <label class="check">
      <input type="checkbox" bind:checked={studio.showGrid} /> show grid
    </label>
    <p class="tip">
      Squint at the picture. Leave the paper areas alone, lay in your lightest pencil everywhere
      else, then build up darker grades one at a time. Save the darkest for last.
    </p>
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
    font-weight: 400;
    font-style: italic;
    font-size: 1.8rem;
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
    color: var(--graphite);
  }
  .field b {
    font-family: var(--display);
    font-size: 1.15rem;
    font-weight: 500;
    color: var(--ink);
  }
  .field i {
    font-family: var(--hand);
    font-style: normal;
    color: var(--sanguine);
  }
  .check {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--graphite);
  }
  .note {
    font-family: var(--hand);
    font-size: 1.15rem;
    line-height: 1.6;
    color: var(--sanguine);
    transform: rotate(-1.5deg);
    transform-origin: left;
  }
  .note.big {
    font-size: 1.4rem;
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
    font-size: 1.1rem;
    cursor: pointer;
  }
  .next:hover {
    background: var(--ink);
    color: var(--paper);
  }
  .levels {
    display: flex;
    gap: 0.4rem;
  }
  .levels button {
    flex: 1;
    padding: 0.35rem 0;
    border: 1px solid var(--rule);
    background: transparent;
    color: var(--graphite);
    font: inherit;
    cursor: pointer;
  }
  .levels button.on {
    border-color: var(--ink);
    color: var(--ink);
  }
  .error {
    color: var(--sanguine);
    font-style: italic;
  }
</style>
