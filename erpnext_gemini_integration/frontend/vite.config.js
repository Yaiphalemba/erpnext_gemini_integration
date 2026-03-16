import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  build: {
    // Output directly to the Frappe app's public folder
    outDir: path.resolve(__dirname, '../erpnext_gemini_integration/public/frontend'),
    emptyOutDir: true, // Clean the folder before every build
    // We disable CSS code splitting so we only get ONE css file to load in hooks.py
    cssCodeSplit: false, 
    rollupOptions: {
      input: path.resolve(__dirname, 'src/main.js'),
      output: {
        // THE PRO MOVE: Disable hashes so the filename is always identical.
        // This saves you from having to dynamically read a manifest.json in Frappe.
        entryFileNames: `js/gemini_app.js`,
        chunkFileNames: `js/[name].js`,
        assetFileNames: `css/gemini_style.[ext]` 
      }
    }
  }
})