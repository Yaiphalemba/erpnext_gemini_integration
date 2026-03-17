import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  build: {
    // Just go up one level and straight into public!
    outDir: path.resolve(__dirname, '../public/frontend'), 
    emptyOutDir: true, 
    cssCodeSplit: false, 
    rollupOptions: {
      input: path.resolve(__dirname, 'src/main.js'),
      output: {
        entryFileNames: `js/gemini_app.js`,
        chunkFileNames: `js/[name].js`,
        assetFileNames: `css/gemini_style.[ext]` 
      }
    }
  }
})