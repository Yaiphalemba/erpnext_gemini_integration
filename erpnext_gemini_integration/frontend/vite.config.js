import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// Get the absolute path to the TRUE Frappe public directory
// We are resolving from the frontend folder, up to the main module folder
const frappePublicDir = path.resolve(__dirname, '../../erpnext_gemini_integration/public/frontend');

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: frappePublicDir, // <-- Use the absolute path!
    emptyOutDir: true,
    cssCodeSplit: false,
    rollupOptions: {
      input: path.resolve(__dirname, 'src/main.js'),
      output: {
        format: 'iife',
        name: 'GeminiApp',
        entryFileNames: `js/gemini_app.js`,
        chunkFileNames: `js/[name].js`,
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'css/gemini_style.[ext]';
          }
          return 'assets/[name].[ext]';
        }
      }
    }
  }
})