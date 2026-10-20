<script lang="ts">
  import Desk from './lib/Desk.svelte'
  import Doodle from './lib/Doodle.svelte'
  import { kingStudy, sphere } from './lib/doodles'
  import Margin from './lib/Margin.svelte'
  import Nav from './lib/Nav.svelte'
  import Plate from './lib/Plate.svelte'
  import Upload from './lib/Upload.svelte'
  import { healthy, OFFLINE } from './lib/api'
  import { studio } from './lib/studio.svelte'

  // say so up front if the api isn't running, instead of after an upload fails
  let offline = $state(false)
  $effect(() => {
    healthy().then((ok) => (offline = !ok))
  })

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
    if (!studio.file || step === 'setup' || step === 'grid' || step === 'values') return
    studio.refreshBlockIn()
  })

  $effect(() => {
    if (studio.current !== 'light' || !studio.file) return
    void studio.bias
    return debounce(() => studio.refreshLight(), 200)
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

  const ball = sphere()
  const king = kingStudy()

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
        <button class="new" onclick={() => studio.reset()}>
          <span class="plus" aria-hidden="true">+</span> start a new drawing
        </button>
      </div>
    {:else}
      <section class="intro">
        <div class="flank left" aria-hidden="true">
          <p class="caption">light from the left</p>
          <Doodle marks={ball} viewBox="0 0 230 175" />
          <p>core shadow, then cast shadow</p>
        </div>

        <div class="center">
          <Upload />
          {#if offline}
            <p class="error">{OFFLINE}</p>
          {:else if studio.error}
            <p class="error">{studio.error}</p>
          {/if}
          <p class="about">
            The grid method is how Albrecht Dürer taught drawing in 1525, looking at his subject
            through a frame strung with threads. Break a picture into squares, block in the big
            shapes, then the shadows, then the lines, then the tones. Every step is the one before it
            with a little more detail.
          </p>
        </div>

        <div class="flank right" aria-hidden="true">
          <p class="caption">the structure of a king</p>
          <Doodle marks={king} viewBox="0 0 300 470" />
          <p>stack the ellipses first</p>
        </div>
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
    min-height: calc(100vh - 3.5rem);
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
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 1rem;
    padding: 0.45rem 1rem 0.35rem;
    border: 1.5px solid var(--sanguine);
    border-radius: 3px 6px 4px 5px;
    background: rgb(138 50 24 / 0.08);
    color: var(--sanguine);
    font-family: var(--script);
    font-size: 1.5rem;
    cursor: pointer;
    transform: rotate(-0.8deg);
    transition: background 0.15s;
  }
  .new:hover {
    background: rgb(138 50 24 / 0.18);
  }
  .plus {
    font-family: var(--display);
    font-size: 1.5rem;
    line-height: 1;
  }
  .intro {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
    align-items: center;
    gap: 1.5rem;
    min-height: calc(100vh - 4rem);
  }
  .center {
    grid-column: 2;
    text-align: center;
  }
  .about {
    max-width: 34rem;
    margin: 1.2rem auto 0;
    color: var(--graphite);
    font-size: 1.08rem;
    line-height: 1.65;
  }
  .flank {
    opacity: 0.85;
  }
  .flank p {
    margin: 0.2rem 0 0;
    font-family: var(--hand);
    -webkit-text-stroke: 0.45px currentColor;
    font-size: 1.5rem;
    color: var(--graphite);
    text-align: center;
  }
  .flank .caption {
    margin-bottom: 0.4rem;
    font-size: 1.7rem;
  }
  .flank.left {
    justify-self: center;
    width: min(190px, 13vw);
    transform: rotate(-3deg);
  }
  .flank.right {
    grid-column: 3;
    justify-self: center;
    width: min(250px, 16vw);
    transform: rotate(2deg);
  }
  .error {
    max-width: 30rem;
    margin: 0.8rem auto 0;
    color: var(--sanguine);
    font-style: italic;
  }
  footer {
    position: fixed;
    z-index: 1;
    left: clamp(1.5rem, 4vw, 4rem);
    bottom: 0.8rem;
    font-size: 0.85rem;
  }
  footer a {
    color: var(--faint);
  }
  /* not enough room for a doodle on both sides: keep the bigger one */
  @media (max-width: 1500px) {
    .intro {
      grid-template-columns: 0 auto minmax(0, 1fr);
      gap: 0 1rem;
    }
    .flank.left {
      display: none;
    }
    .flank.right {
      width: min(230px, 100%);
    }
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
    .flank {
      display: none;
    }
    .intro {
      display: block;
      min-height: 0;
    }
    footer {
      position: static;
      margin-top: 2rem;
    }
  }
</style>
