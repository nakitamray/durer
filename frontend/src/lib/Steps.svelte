<script lang="ts">
  import { studio, STEPS } from './studio.svelte'
  import { line } from './sketch'

  const underline = line(2, 4, 118, 3, { roughness: 1.4, bowing: 2, seed: 11, width: 1.6 })
</script>

<nav>
  <ol>
    {#each STEPS as s, i}
      <li>
        <button
          class:current={studio.step === i}
          disabled={i > 0 && !studio.file}
          onclick={() => (studio.step = i)}
        >
          <span class="numeral">{s.numeral}.</span>
          <span class="name">{s.name}</span>
          <span class="sub">{s.sub}</span>
          {#if studio.step === i}
            <svg viewBox="0 0 120 8" aria-hidden="true">
              {#each underline as u}
                <path d={u.d} stroke="var(--sanguine)" stroke-width={u.width} fill="none" />
              {/each}
            </svg>
          {/if}
        </button>
      </li>
    {/each}
  </ol>
</nav>

<style>
  ol {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem 2.2rem;
    margin: 0;
    padding: 0;
    list-style: none;
  }
  button {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    padding: 0.2rem 0 0.7rem;
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
    font-family: var(--display);
    font-size: 0.85rem;
    letter-spacing: 0.08em;
  }
  .name {
    font-family: var(--display);
    font-style: italic;
    font-size: 1.35rem;
    line-height: 1.1;
  }
  .sub {
    font-size: 0.8rem;
    color: var(--faint);
  }
  svg {
    position: absolute;
    left: -2px;
    bottom: 0;
    width: 7rem;
    height: 0.5rem;
    overflow: visible;
  }
</style>
