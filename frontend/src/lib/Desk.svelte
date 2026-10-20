<script lang="ts">
  import Doodle from './Doodle.svelte'
  import { eraser, fineliner, scaffold } from './doodles'

  // things lying on the sketchbook, and the leftover construction lines under everything
  const lines = scaffold(1440, 900)
  const pen = fineliner()
  const rubber = eraser()
</script>

<div class="desk" aria-hidden="true">
  <Doodle marks={lines} viewBox="0 0 1440 900" class="scaffold" />
</div>
<div class="objects" aria-hidden="true">
  <Doodle marks={pen} viewBox="0 0 510 60" class="pen" />
  <Doodle marks={rubber} viewBox="-40 0 240 120" class="eraser" />
</div>

<style>
  .desk {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.35;
  }
  .desk :global(.scaffold) {
    width: 100%;
    height: 100%;
  }
  .objects {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
  }
  .objects :global(.pen) {
    position: absolute;
    width: 420px;
    right: -70px;
    bottom: 50px;
    transform: rotate(-24deg);
    filter: drop-shadow(6px 10px 6px rgb(40 22 8 / 0.35));
  }
  .objects :global(.eraser) {
    position: absolute;
    width: 170px;
    right: -30px;
    top: -6px;
    transform: rotate(24deg);
    filter: drop-shadow(5px 8px 5px rgb(40 22 8 / 0.3));
  }
  @media (max-width: 900px) {
    .objects {
      display: none;
    }
  }
</style>
