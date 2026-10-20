<script lang="ts">
  import { studio } from './studio.svelte'
  import { path } from './sketch'

  let dragging = $state(false)
  let input: HTMLInputElement

  const arch = [
    ...path('M 30 330 L 30 150 A 130 130 0 0 1 290 150 L 290 330', { seed: 4, width: 1.3 }),
    ...path('M 52 330 L 52 152 A 108 108 0 0 1 268 152 L 268 330', { seed: 9, width: 0.7, roughness: 1 }),
    ...path('M 14 330 L 306 330', { seed: 2, width: 1.1 }),
    ...path('M 30 150 L 290 150', { seed: 7, width: 0.5, roughness: 1.2 }),
  ]

  function pick(files: FileList | null | undefined) {
    const file = files?.[0]
    if (file) studio.load(file)
  }

  function onDrop(e: DragEvent) {
    e.preventDefault()
    dragging = false
    pick(e.dataTransfer?.files)
  }
</script>

<button
  class="drop"
  class:dragging
  onclick={() => input.click()}
  ondragover={(e) => {
    e.preventDefault()
    dragging = true
  }}
  ondragleave={() => (dragging = false)}
  ondrop={onDrop}
>
  <svg viewBox="0 0 320 340" aria-hidden="true">
    {#each arch as s}
      <path d={s.d} stroke={s.stroke} stroke-width={s.width} fill="none" />
    {/each}
  </svg>
  <span class="inside">
    <span class="title">Choose a subject</span>
    <span class="hint">drop an image here, or click to browse</span>
    <span class="note">a photo, a painting, an old sketch…</span>
  </span>
</button>

<input
  bind:this={input}
  type="file"
  accept="image/*"
  hidden
  onchange={(e) => pick(e.currentTarget.files)}
/>

<style>
  .drop {
    position: relative;
    display: block;
    width: min(340px, 100%);
    margin: 0 auto;
    padding: 0;
    border: 0;
    background: none;
    color: var(--ink);
    font: inherit;
    cursor: pointer;
    transition: color 0.2s;
  }
  .drop:hover,
  .dragging {
    color: var(--sanguine);
  }
  svg {
    display: block;
    width: 100%;
    overflow: visible;
  }
  .inside {
    position: absolute;
    inset: 46% 18% 8%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
    text-align: center;
  }
  .title {
    font-family: var(--display);
    font-style: italic;
    font-size: 1.7rem;
  }
  .hint {
    color: var(--graphite);
    font-size: 0.95rem;
  }
  .note {
    margin-top: 0.6rem;
    font-family: var(--hand);
    font-size: 1.15rem;
    color: var(--faint);
    transform: rotate(-3deg);
  }
</style>
