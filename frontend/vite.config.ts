import { svelte } from '@sveltejs/vite-plugin-svelte'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      '/api': {
        // 127.0.0.1, not localhost: on Windows node tries ::1 first and uvicorn
        // only listens on ipv4, so the proxy gets refused
        target: 'http://127.0.0.1:8000',
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
