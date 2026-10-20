<script lang="ts">
  import { studio } from './studio.svelte'
  import { line, path, rect, type Stroke } from './sketch'

  let dragging = $state(false)
  let input: HTMLInputElement

  // the card sits at x 130-510, y 70-330 inside a 640 × 400 drawing
  const [L, T, R, B] = [130, 70, 510, 330]
  const marks: Stroke[] = [
    // dimension line across the top, with extension lines up from the card
    ...line(L, 36, R, 36, { seed: 1, width: 0.9 }),
    ...line(L, 28, L, 62, { seed: 2, width: 0.6 }),
    ...line(R, 28, R, 62, { seed: 3, width: 0.6 }),
    ...line(L, 36, L + 10, 31, { seed: 4, width: 0.9 }),
    ...line(L, 36, L + 10, 41, { seed: 5, width: 0.9 }),
    ...line(R, 36, R - 10, 31, { seed: 6, width: 0.9 }),
    ...line(R, 36, R - 10, 41, { seed: 7, width: 0.9 }),
    // and one down the right side
    ...line(548, T, 548, B, { seed: 8, width: 0.9 }),
    ...line(518, T, 558, T, { seed: 9, width: 0.6 }),
    ...line(518, B, 558, B, { seed: 10, width: 0.6 }),
    ...line(548, T, 543, T + 10, { seed: 11, width: 0.9 }),
    ...line(548, T, 553, T + 10, { seed: 12, width: 0.9 }),
    ...line(548, B, 543, B - 10, { seed: 13, width: 0.9 }),
    ...line(548, B, 553, B - 10, { seed: 14, width: 0.9 }),
    // crop marks off each corner
    ...[
      [L, T, -1, -1],
      [R, T, 1, -1],
      [L, B, -1, 1],
      [R, B, 1, 1],
    ].flatMap(([x, y, dx, dy], i) => [
      ...line(x + dx * 8, y, x + dx * 26, y, { seed: 20 + i, width: 0.7 }),
      ...line(x, y + dy * 8, x, y + dy * 26, { seed: 30 + i, width: 0.7 }),
    ]),
    // centre ticks, like registration marks
    ...line((L + R) / 2, B + 8, (L + R) / 2, B + 22, { seed: 40, width: 0.7 }),
    ...line(L - 22, (T + B) / 2, L - 8, (T + B) / 2, { seed: 41, width: 0.7 }),
  ]
  const arrows = [
    // from "start here" round to the top left corner
    ...path('M 64 40 Q 92 46 112 66', { seed: 50, width: 1.3 }),
    ...line(112, 66, 101, 63, { seed: 51, width: 1.3 }),
    ...line(112, 66, 110, 55, { seed: 52, width: 1.3 }),
    // little pointers in from the notes at the sides
    ...path('M 84 170 Q 104 172 118 180', { seed: 53, width: 0.9 }),
    ...path('M 92 238 Q 108 236 118 228', { seed: 54, width: 0.9 }),
    ...path('M 560 186 Q 536 190 522 200', { seed: 55, width: 0.9 }),
  ]
  const icon = [
    ...rect(4, 4, 64, 46, { seed: 60, width: 1.3 }),
    ...path('M 8 44 L 26 24 L 38 36 L 46 28 L 64 44', { seed: 61, width: 1.1 }),
    ...path('M 50 16 A 5 5 0 1 1 49.9 16', { seed: 62, width: 1 }),
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

<div class="wrap">
  <svg class="marks" viewBox="0 0 640 400" aria-hidden="true">
    {#each marks as m}<path d={m.d} stroke-width={m.width} />{/each}
    <g class="arrows">
      {#each arrows as m}<path d={m.d} stroke-width={m.width} />{/each}
    </g>
  </svg>

  <span class="label width">any width</span>
  <span class="label height">any height</span>
  <span class="note start">start here</span>
  <span class="note n1">a photo</span>
  <span class="note n2">a painting</span>
  <span class="note n3">an old sketch</span>
  <span class="note n4">your own work</span>
  <span class="note n5">the bigger the better</span>
  <span class="note n6">jpg, png or webp</span>

  <button
    class="card"
    class:dragging
    onclick={() => input.click()}
    ondragover={(e) => {
      e.preventDefault()
      dragging = true
    }}
    ondragleave={() => (dragging = false)}
    ondrop={onDrop}
  >
    <span class="tape a" aria-hidden="true"></span>
    <span class="tape b" aria-hidden="true"></span>
    <svg class="icon" viewBox="0 0 72 54" aria-hidden="true">
      {#each icon as m}<path d={m.d} stroke-width={m.width} />{/each}
    </svg>
    <span class="title">Choose a picture</span>
    <span class="hint">drop it anywhere on this card, or</span>
    <span class="browse">browse your files</span>
  </button>
</div>

<input
  bind:this={input}
  type="file"
  accept="image/*"
  hidden
  onchange={(e) => pick(e.currentTarget.files)}
/>

<style>
  .wrap {
    position: relative;
    width: 640px;
    height: 400px;
    /* room for the notes that hang off either side */
    margin: 0 80px;
  }
  .marks {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    overflow: visible;
    pointer-events: none;
    color: var(--graphite);
  }
  .marks path {
    fill: none;
    stroke: currentColor;
    stroke-linecap: round;
  }
  .arrows {
    color: var(--sanguine);
  }
  .label,
  .note {
    position: absolute;
    font-family: var(--script);
    line-height: 1;
    white-space: nowrap;
    pointer-events: none;
  }
  .label {
    font-size: 1.15rem;
    color: var(--graphite);
  }
  .label.width {
    top: 4px;
    left: 50%;
    transform: translateX(-50%);
  }
  .label.height {
    top: 200px;
    left: 566px;
    transform: translateY(-50%) rotate(90deg);
    transform-origin: left center;
  }
  .note {
    color: var(--graphite);
  }
  .start {
    top: 6px;
    left: -40px;
    font-size: 2.3rem;
    font-weight: 600;
    color: var(--sanguine);
    transform: rotate(-9deg);
  }
  .n1 {
    top: 156px;
    left: 18px;
    font-size: 1.5rem;
    transform: rotate(-4deg);
  }
  .n2 {
    top: 240px;
    left: -6px;
    font-size: 2rem;
    transform: rotate(3deg);
  }
  .n3 {
    top: 120px;
    left: 572px;
    font-size: 1.35rem;
    transform: rotate(5deg);
  }
  .n4 {
    top: 172px;
    left: 568px;
    font-size: 1.75rem;
    transform: rotate(-3deg);
  }
  .n5 {
    top: 356px;
    left: 150px;
    font-size: 1.4rem;
    transform: rotate(-2deg);
  }
  .n6 {
    top: 360px;
    left: 410px;
    font-size: 1.1rem;
    color: var(--faint);
  }

  .card {
    position: absolute;
    left: 130px;
    top: 70px;
    width: 380px;
    height: 260px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.35rem;
    padding: 0;
    border: 0;
    border-radius: 2px;
    background: var(--sheet);
    color: var(--ink);
    font: inherit;
    cursor: pointer;
    transform: rotate(-0.6deg);
    box-shadow:
      0 18px 30px -18px rgb(40 22 8 / 0.65),
      0 2px 5px rgb(40 22 8 / 0.25);
    transition:
      transform 0.2s,
      box-shadow 0.2s;
  }
  /* the dashed drop area inside the card */
  .card::before {
    content: '';
    position: absolute;
    inset: 14px;
    border: 1.5px dashed rgb(34 22 13 / 0.35);
    border-radius: 3px;
    transition: border-color 0.2s;
  }
  .card:hover,
  .card.dragging {
    transform: rotate(-0.6deg) translateY(-3px);
    box-shadow:
      0 24px 36px -18px rgb(40 22 8 / 0.7),
      0 3px 7px rgb(40 22 8 / 0.25);
  }
  .card:hover::before,
  .card.dragging::before {
    border-color: var(--sanguine);
  }
  .tape {
    position: absolute;
    width: 4.8rem;
    height: 1.4rem;
    background: rgb(232 222 196 / 0.75);
    box-shadow: 0 1px 2px rgb(40 22 8 / 0.2);
  }
  .tape.a {
    top: -0.6rem;
    left: -1.4rem;
    transform: rotate(-32deg);
  }
  .tape.b {
    bottom: -0.5rem;
    right: -1.4rem;
    transform: rotate(-30deg);
  }
  .icon {
    width: 64px;
    margin-bottom: 0.2rem;
    overflow: visible;
    color: var(--graphite);
  }
  .icon path {
    fill: none;
    stroke: currentColor;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
  .title {
    font-family: var(--script);
    font-size: 2.6rem;
    font-weight: 600;
    line-height: 1;
  }
  .hint {
    font-family: var(--script);
    font-size: 1.3rem;
    color: var(--graphite);
  }
  .browse {
    margin-top: 0.3rem;
    padding: 0.2rem 1rem 0.3rem;
    border: 1.5px solid var(--ink);
    border-radius: 3px 5px 4px 6px;
    font-family: var(--script);
    font-size: 1.35rem;
    transition:
      background 0.15s,
      color 0.15s;
  }
  .card:hover .browse {
    background: var(--ink);
    color: var(--sheet);
  }

  @media (max-width: 1240px) {
    .n3,
    .n4 {
      display: none;
    }
  }
  @media (max-width: 900px) {
    .wrap {
      width: 100%;
      height: auto;
      margin: 0;
    }
    .marks,
    .label,
    .note {
      display: none;
    }
    .card {
      position: relative;
      left: 0;
      top: 0;
      width: 100%;
      height: 240px;
    }
  }
</style>
