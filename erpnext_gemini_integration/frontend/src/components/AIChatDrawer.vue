<script setup>
import { defineEmits, ref, watch, nextTick } from 'vue'
import { useChatEngine } from '../composables/useChatEngine'
import MessageThread from './MessageThread.vue'
import CommandInput from './CommandInput.vue'

const emit = defineEmits(['close'])
const { chatHistory, isThinking, sendMessage } = useChatEngine()
const threadContainer = ref(null)

// Auto-scroll using nextTick (The clean Vue way)
watch(chatHistory, () => {
  nextTick(() => {
    if (threadContainer.value) {
      threadContainer.value.scrollTop = threadContainer.value.scrollHeight
    }
  })
}, { deep: true })

const handleSend = (text) => sendMessage(text)
</script>

<template>
  <aside class="fixed bottom-24 right-6 w-[400px] h-[700px] max-h-[80vh] bg-slate-900/95 backdrop-blur-xl shadow-2xl z-[9999] rounded-2xl border border-white/10 flex flex-col overflow-hidden ring-1 ring-white/5">
    
    <header class="p-4 border-b border-white/10 flex justify-between items-center bg-slate-800/50">
      <div class="flex items-center gap-3">
        <span class="relative flex h-3 w-3">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-3 w-3 bg-orange-500"></span>
        </span>
        <h2 class="text-xs font-bold tracking-widest text-slate-200 uppercase">AI Analyst</h2>
      </div>
      
      <button @click="emit('close')" class="text-slate-400 hover:text-orange-500 hover:bg-slate-800 p-1 rounded transition-colors">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </header>

    <div ref="threadContainer" class="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide bg-gradient-to-b from-slate-900/50 to-slate-900">
      <MessageThread :messages="chatHistory" :isThinking="isThinking" />
    </div>

    <div class="p-4 border-t border-white/10 bg-slate-900 shadow-[0_-10px_40px_rgba(0,0,0,0.3)]">
      <CommandInput @submit="handleSend" :disabled="isThinking" />
    </div>
  </aside>
</template>