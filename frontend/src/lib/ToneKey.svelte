<script lang="ts">
  import { percent } from './format'
  import type { Tone } from './types'

  let { tones }: { tones: Tone[] } = $props()

  // lightest first, the order you'd lay them down
  const ordered = $derived([...tones].reverse())
</script>

<ol class="key">
  {#each ordered as t, i}
    <li>
      <span class="swatch" style:background="rgb({t.gray} {t.gray} {t.gray})"></span>
      <span class="grade" class:paper={t.grade === 'paper'}>{t.grade}</span>
      <span class="cover">{percent(t.coverage)} of the picture</span>
      <span class="order">{t.grade === 'paper' ? 'leave it' : i}</span>
    </li>
  {/each}
</ol>

<style>
  .key {
    list-style: none;
    margin: 0.8rem 0;
    padding: 0;
  }
  li {
    display: grid;
    grid-template-columns: 2.6rem 2.6rem 1fr auto;
    align-items: center;
    gap: 0.6rem;
    padding: 0.35rem 0;
    border-bottom: 1px solid var(--rule);
  }
  .swatch {
    height: 1.6rem;
    border-radius: 1px 3px 2px 2px;
    box-shadow: inset 0 0 0 1px rgb(0 0 0 / 0.12);
  }
  .grade {
    font-family: var(--display);
    font-size: 1.2rem;
    font-weight: 500;
  }
  .grade.paper {
    font-style: italic;
    font-weight: 400;
    font-size: 1rem;
  }
  .cover {
    color: var(--graphite);
    font-size: 0.9rem;
  }
  .order {
    font-family: var(--hand);
    color: var(--sanguine);
    font-size: 1.1rem;
  }
</style>
