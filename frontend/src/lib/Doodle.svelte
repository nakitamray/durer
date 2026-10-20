<script lang="ts">
  import type { Mark } from './doodles'

  let {
    marks,
    viewBox,
    class: cls = '',
    label = '',
  }: { marks: Mark[]; viewBox: string; class?: string; label?: string } = $props()
</script>

<svg {viewBox} class={cls} role={label ? 'img' : undefined} aria-label={label || undefined} aria-hidden={!label}>
  {#each marks as m}
    <path d={m.d} stroke={m.stroke} fill={m.fill} stroke-width={m.width} stroke-linecap="round" />
  {/each}
</svg>

<style>
  svg {
    display: block;
    overflow: visible;
  }
</style>
