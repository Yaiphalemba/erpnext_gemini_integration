import { createApp } from 'vue'
import App from './App.vue'
import './style.css' // Your Tailwind CSS file

// Wait for Frappe to finish loading the desk
document.addEventListener('DOMContentLoaded', () => {
  
  // 1. Create a hidden wrapper div for our AI drawer
  const geminiWrapper = document.createElement('div')
  geminiWrapper.id = 'gemini-ai-workspace'
  
  // 2. Append it right to the body so it sits above everything
  document.body.appendChild(geminiWrapper)

  // 3. Mount our beautiful cinematic Vue app to it
  const app = createApp(App)
  app.mount('#gemini-ai-workspace')

  console.log("Gemini Analyst Drawer Initialized. Ready to crush some data.")
})