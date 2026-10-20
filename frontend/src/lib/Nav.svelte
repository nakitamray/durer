<script lang="ts">
  import Doodle from './Doodle.svelte'
  import { sphere, valueScale } from './doodles'
  import { line, path } from './sketch'
  import { studio, STEPS } from './studio.svelte'

  const rule = [
    ...line(0, 4, 200, 6, { seed: 5, roughness: 0.8, bowing: 1 }),
    ...line(4, 10, 196, 9, { seed: 6, roughness: 0.8, width: 0.5 }),
  ]
  const arrow = [
    ...path('M2 9 Q 14 4 26 8', { seed: 31, width: 1.4 }),
    ...line(26, 8, 19, 3, { seed: 32, width: 1.4 }),
    ...line(26, 8, 20, 13, { seed: 33, width: 1.4 }),
  ]

  const ball = sphere()
  const scale = valueScale()
</script>

<aside class="side">
  <header>
    <h1>Dürer</h1>
    <p class="tagline">draw anything one square at a time</p>
    <svg class="rule" viewBox="0 0 200 12" preserveAspectRatio="none" aria-hidden="true">
      {#each rule as r}<path d={r.d} stroke="currentColor" stroke-width={r.width} fill="none" />{/each}
    </svg>
  </header>

  <nav>
    <ol>
      {#each STEPS as s, i}
        <li>
          <button
            class:current={studio.step === i}
            disabled={i > 0 && !studio.file}
            onclick={() => (studio.step = i)}
          >
            {#if studio.step === i}
              <svg class="arrow" viewBox="0 0 28 16" aria-hidden="true">
                {#each arrow as a}<path d={a.d} stroke="currentColor" stroke-width={a.width} fill="none" />{/each}
              </svg>
            {/if}
            <span class="numeral">{s.numeral}</span>
            <span class="name">{s.name}</span>
            <span class="sub">{s.sub}</span>
          </button>
        </li>
      {/each}
    </ol>
  </nav>

  <div class="studies" aria-hidden="true">
    <Doodle marks={ball} viewBox="0 0 230 175" class="ball" />
    <p class="scrawl">light from the left</p>
    <Doodle marks={scale} viewBox="0 0 230 46" class="scale" />
  </div>
</aside>

<style>
  .side {
    position: relative;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  h1 {
    margin: 0;
    font-family: var(--display);
    font-weight: 500;
    font-size: 3.4rem;
    line-height: 0.9;
    letter-spacing: 0.01em;
  }
  .tagline {
    margin: 0.4rem 0 0;
    font-family: var(--hand);
    -webkit-text-stroke: 0.45px currentColor;
    font-size: 1.9rem;
    line-height: 1.1;
    color: var(--graphite);
  }
  .rule {
    display: block;
    width: 100%;
    height: 12px;
    margin-top: 0.6rem;
    color: var(--ink);
  }
  ol {
    margin: 0;
    padding: 0;
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }
  button {
    position: relative;
    display: grid;
    grid-template-columns: 2.3rem 1fr;
    align-items: baseline;
    width: 100%;
    padding: 0.2rem 0;
    border: 0;
    background: none;
    color: var(--graphite);
    font: inherit;
    text-align: left;
    cursor: pointer;
  }
  button:disabled {
    color: var(--faint);
    cursor: default;
  }
  button:not(:disabled):hover,
  .current {
    color: var(--ink);
  }
  .numeral {
    grid-row: span 2;
    font-family: var(--display);
    font-size: 0.85rem;
    letter-spacing: 0.06em;
  }
  .name {
    font-family: var(--display);
    font-style: italic;
    font-size: 1.25rem;
    line-height: 1.05;
  }
  .current .name {
    font-weight: 500;
  }
  .sub {
    font-size: 0.8rem;
    color: var(--faint);
  }
  .current .sub {
    color: var(--graphite);
  }
  .arrow {
    position: absolute;
    left: -2.1rem;
    top: 0.55rem;
    width: 1.8rem;
    color: var(--sanguine);
  }
  .studies {
    position: relative;
    margin-top: 1.6rem;
    opacity: 0.8;
  }
  .studies :global(.ball) {
    width: 150px;
  }
  .scrawl {
    position: absolute;
    top: -1.2rem;
    left: 2.4rem;
    white-space: nowrap;
    margin: 0;
    font-family: var(--hand);
    -webkit-text-stroke: 0.45px currentColor;
    font-size: 1.45rem;
    color: var(--graphite);
    transform: rotate(-8deg);
  }
  .studies :global(.scale) {
    width: 150px;
    margin-top: 0.8rem;
  }
  @media (max-height: 880px) {
    .studies {
      margin-top: 1rem;
    }
    .studies :global(.ball) {
      width: 105px;
    }
    .studies :global(.scale) {
      width: 110px;
      margin-top: 0.4rem;
    }
    .scrawl {
      font-size: 1.2rem;
    }
  }
  @media (max-height: 800px) {
    .studies {
      display: none;
    }
  }
  @media (max-width: 900px) {
    .side {
      gap: 0.8rem;
    }
    h1 {
      font-size: 2.6rem;
    }
    ol {
      flex-direction: row;
      overflow-x: auto;
      gap: 1.2rem;
      padding-bottom: 0.4rem;
    }
    li {
      flex: none;
    }
    .arrow,
    .studies {
      display: none;
    }
    .current .name {
      text-decoration: underline;
      text-decoration-color: var(--sanguine);
    }
  }
</style>
