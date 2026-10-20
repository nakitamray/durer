<script lang="ts">
  import Desk from './lib/Desk.svelte'
  import Doodle from './lib/Doodle.svelte'
  import { cube, durerFrame } from './lib/doodles'
  import Margin from './lib/Margin.svelte'
  import Nav from './lib/Nav.svelte'
  import Plate from './lib/Plate.svelte'
  import Upload from './lib/Upload.svelte'
  import { studio } from './lib/studio.svelte'

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
    const step = studio.current
    if (!studio.file) return
    if (step === 'place' || step === 'big' || step === 'medium' || step === 'notan' || step === 'contour') {
      studio.refreshBlockIn()
    }
  })

  $effect(() => {
    if (studio.current !== 'big' || !studio.solids || !studio.file) return
    void studio.simplicity
    return debounce(() => studio.refreshShapes(), 200)
  })

  $effect(() => {
    if (studio.current !== 'notan' || !studio.file) return
    void studio.bias
    return debounce(() => studio.refreshNotan(), 200)
  })

  $effect(() => {
    if (studio.current !== 'contour' || !studio.file) return
    void studio.detail
    return debounce(() => studio.refreshContour(), 200)
  })

  $effect(() => {
    if (studio.current !== 'values' || !studio.file) return
    void studio.levels
    return debounce(() => studio.refreshValues(), 200)
  })

  const frame = durerFrame()
  const box = cube()

  // past the grid the photo fades back so the drawing on top can show
  let faded = false
  $effect(() => {
    if (studio.step >= 2 && !faded) {
      faded = true
      studio.refOpacity = 0.35
    }
  })
</script>

<Desk />

<div class="book">
  <Nav />

  <main class:empty={!studio.src}>
    {#if studio.src}
      <section class="stage">
        <Plate />
        {#if studio.loading}<p class="working">working</p>{/if}
      </section>
      <div class="notes">
        <Margin />
        <button class="new" onclick={() => studio.reset()}>start over with a new picture</button>
      </div>
    {:else}
      <section class="intro">
        <Upload />
        <p class="about">
          The grid method is how Albrecht Dürer taught drawing in 1525, looking at his subject
          through a frame strung with threads. Break a picture into squares, block in the big shapes,
          then the shadows, then the lines, then the tones. Every step is the one before it with a
          little more detail.
        </p>
        <p class="scribble">start here</p>
        <div class="aside left" aria-hidden="true">
          <Doodle marks={frame} viewBox="-10 0 250 200" />
          <p>his frame and threads</p>
        </div>
        <div class="aside right" aria-hidden="true">
          <Doodle marks={box} viewBox="0 20 260 170" />
          <p>big shapes first</p>
        </div>
        {#if studio.error}<p class="error">{studio.error}</p>{/if}
      </section>
    {/if}
  </main>
</div>

<footer>
  <a href="https://github.com/nakitamray/durer">source</a>
</footer>

<style>
  .book {
    position: relative;
    z-index: 1;
    display: grid;
    grid-template-columns: 220px minmax(0, 1fr);
    gap: 3rem;
    min-height: calc(100vh - 3rem);
  }
  main {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 290px;
    gap: 2.5rem;
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
    top: -0.4rem;
    right: 0;
    margin: 0;
    font-family: var(--hand);
    -webkit-text-stroke: 0.45px currentColor;
    font-size: 1.5rem;
    color: var(--sanguine);
    animation: breathe 1.4s ease-in-out infinite;
  }
  @keyframes breathe {
    50% {
      opacity: 0.35;
    }
  }
  .notes {
    padding-top: 0.6rem;
  }
  .new {
    margin-top: 2.5rem;
    padding: 0;
    border: 0;
    background: none;
    color: var(--faint);
    font: inherit;
    font-style: italic;
    cursor: pointer;
  }
  .new:hover {
    color: var(--sanguine);
  }
  .intro {
    position: relative;
    max-width: 36rem;
    margin: 4vh auto 0;
    text-align: center;
  }
  .about {
    margin-top: 2.2rem;
    color: var(--graphite);
    font-size: 1.1rem;
    line-height: 1.7;
  }
  .scribble {
    position: absolute;
    top: 2rem;
    left: -3rem;
    margin: 0;
    font-family: var(--hand);
    -webkit-text-stroke: 0.45px currentColor;
    font-size: 2.6rem;
    color: var(--sanguine);
    transform: rotate(-14deg);
  }
  .aside {
    position: absolute;
    width: 200px;
    opacity: 0.85;
  }
  .aside p {
    margin: 0.2rem 0 0;
    font-family: var(--hand);
    -webkit-text-stroke: 0.45px currentColor;
    font-size: 1.5rem;
    color: var(--graphite);
  }
  .aside.left {
    top: 21rem;
    right: calc(100% + 3rem);
    transform: rotate(-3deg);
  }
  .aside.right {
    top: 3rem;
    left: calc(100% + 3rem);
    transform: rotate(4deg);
  }
  .error {
    color: var(--sanguine);
    font-style: italic;
  }
  footer {
    position: relative;
    z-index: 1;
    margin-top: 3rem;
    text-align: right;
    font-size: 0.9rem;
  }
  footer a {
    color: var(--faint);
  }
  @media (max-width: 1180px) {
    main {
      grid-template-columns: minmax(0, 1fr);
    }
  }
  @media (max-width: 900px) {
    .book {
      grid-template-columns: minmax(0, 1fr);
      gap: 1.5rem;
    }
    .scribble,
    .aside {
      display: none;
    }
  }
</style>
