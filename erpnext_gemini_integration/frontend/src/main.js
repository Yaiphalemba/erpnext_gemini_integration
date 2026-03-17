// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

const mountId = 'gemini-chat-drawer';
let mountEl = document.getElementById(mountId);

// If Frappe doesn't have the element, build it yourself
if (!mountEl) {
    mountEl = document.createElement('div');
    mountEl.id = mountId;
    document.body.appendChild(mountEl);
}

createApp(App).mount(mountEl);
console.log("Gemini Analyst Drawer Initialized. Ready to crush some data.")