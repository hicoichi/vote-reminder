import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  // GitHub Pages（https://<owner>.github.io/vote-reminder/）配信用のベースパス
  base: '/vote-reminder/',
  plugins: [vue()],
})
