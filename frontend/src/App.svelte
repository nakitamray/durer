<script lang="ts">
  import Margin from './lib/Margin.svelte'
  import Plate from './lib/Plate.svelte'
  import Steps from './lib/Steps.svelte'
  import Upload from './lib/Upload.svelte'
  import { line } from './lib/sketch'
  import { studio } from './lib/studio.svelte'

  const rule = [
    ...line(0, 3, 1000, 4, { seed: 5, roughness: 0.5, bowing: 0.3 }),
    ...line(0, 8, 1000, 7, { seed: 6, roughness: 0.5, bowing: 0.3, width: 0.5 }),
  ]

  function debounce(fn: () => void, ms: number) {
    const t = setTimeout(fn, ms)
    return () => clearTimeout(t)
  }

  $effect(() => {
    // touch everything the grid depends on so the effect tracks it
    const deps = [studio.file, studio.paper, studio.cols]
    if (!deps[0]) return
    return debounce(() => studio.refreshGrid(), 150)
  })

  $effect(() => {
    if (studio.step !== 2 || !studio.file) return
    void studio.detail
    return debounce(() => studio.refreshContour(), 200)
  })

  $effect(() => {
    if (studio.step !== 3 || !studio.file) return
    void studio.levels
    return debounce(() => studio.refreshValues(), 200)
  })

  let fadedOnce = false
  $effect(() => {
    if (studio.step === 2 && !fadedOnce) {
      fadedOnce = true
      studio.refOpacity = 0.3
    }
  })
</script>

<header>
  <div class="brand">
    <h1>Dürer</h1>
    <p class="tagline">draw anything, one square at a time</p>
  </div>
  {#if studio.file}
    <button class="new" onclick={() => studio.reset()}>start over</button>
  {/if}
</header>

<svg class="rule" viewBox="0 0 1000 10" preserveAspectRatio="none" aria-hidden="true">
  {#each rule as r}
    <path d={r.d} stroke="currentColor" stroke-width={r.width} fill="none" />
  {/each}
</svg>

<Steps />

<main class:empty={!studio.src}>
  {#if studio.src}
    <section class="stage">
      <Plate />
      {#if studio.loading}<p class="working">working…</p>{/if}
    </section>
    <Margin />
  {:else}
    <section class="intro">
      <Upload />
      <p class="about">
        The grid method is how Albrecht Dürer taught perspective in 1525, looking through a frame
        strung with threads. Break a picture into squares, copy one square at a time, and the
        proportions take care of themselves.
      </p>
      {#if studio.error}<p class="error">{studio.error}</p>{/if}
    </section>
  {/if}
</main>

<footer>
  <span>Dürer</span>
  <span class="dot">·</span>
  <a href="https://github.com/nakitamray/durer">source</a>
</footer>

<style>
  header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 1rem;
  }
  h1 {
    margin: 0;
    font-family: var(--display);
    font-weight: 400;
    font-size: clamp(2.8rem, 6vw, 4.2rem);
    letter-spacing: 0.01em;
    line-height: 1;
  }
  .tagline {
    margin: 0.2rem 0 0 0.2rem;
    font-family: var(--hand);
    font-size: 1.25rem;
    color: var(--graphite);
  }
  .new {
    padding: 0;
    border: 0;
    background: none;
    color: var(--graphite);
    font: inherit;
    font-style: italic;
    white-space: nowrap;
    cursor: pointer;
  }
  .new:hover {
    color: var(--sanguine);
  }
  .rule {
    display: block;
    width: 100%;
    height: 10px;
    margin: 1rem 0 1.4rem;
    color: var(--ink);
  }
  main {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 300px;
    gap: 3rem;
    margin-top: 2rem;
    align-items: start;
  }
  main.empty {
    display: block;
  }
  .stage {
    position: relative;
    padding: 1.6rem 0 0 1.6rem;
  }
  .working {
    position: absolute;
    top: 0;
    right: 0;
    margin: 0;
    font-family: var(--hand);
    color: var(--sanguine);
  }
  .intro {
    max-width: 34rem;
    margin: 1rem auto 0;
    text-align: center;
  }
  .about {
    margin-top: 2.5rem;
    color: var(--graphite);
    font-size: 1.05rem;
    line-height: 1.7;
  }
  .error {
    color: var(--sanguine);
    font-style: italic;
  }
  footer {
    margin-top: 5rem;
    padding-top: 1rem;
    border-top: 1px solid var(--rule);
    color: var(--faint);
    font-size: 0.9rem;
    display: flex;
    gap: 0.5rem;
  }
  footer a {
    color: inherit;
  }
  @media (max-width: 860px) {
    main {
      grid-template-columns: 1fr;
      gap: 2rem;
    }
  }
</style>
