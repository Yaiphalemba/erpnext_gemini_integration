<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue'
import { useChatEngine } from '../composables/useChatEngine'
import MessageThread from './MessageThread.vue'
import CommandInput from './CommandInput.vue'

const props = defineProps({ isOpen: Boolean })
const emit = defineEmits(['close'])

// Initialize our brain
const { chatHistory, isThinking, sendMessage } = useChatEngine()

// Auto-scroll logic (so the chat always stays at the bottom when a new message arrives)
const threadContainer = ref(null)
watch(chatHistory, () => {
  setTimeout(() => {
    if (threadContainer.value) {
      threadContainer.value.scrollTop = threadContainer.value.scrollHeight
    }
  }, 100) // Small delay to let Vue render the DOM first
}, { deep: true })

const handleSend = (text) => {
  sendMessage(text)
}
</script>

<template>
  <div v-if="isOpen" 
       class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-40 transition-opacity"
       @click="emit('close')">
  </div>

  <aside :class="[
      'fixed top-0 right-0 h-full w-[450px] bg-slate-900 shadow-2xl z-50 transform transition-transform duration-300 ease-in-out border-l border-white/10 flex flex-col',
      isOpen ? 'translate-x-0' : 'translate-x-full'
    ]">
    
    <header class="p-4 border-b border-white/10 flex justify-between items-center bg-slate-900/80 backdrop-blur-md">
      <h2 class="text-sm font-semibold tracking-wider text-slate-300 uppercase">Data Analyst</h2>
      <button @click="emit('close')" class="text-slate-400 hover:text-orange-400 transition-colors">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
      </button>
    </header>

    <div ref="threadContainer" class="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide">
      <MessageThread :messages="chatHistory" :isThinking="isThinking" />
    </div>

    <div class="p-4 border-t border-white/10 bg-slate-900">
      <CommandInput @submit="handleSend" :disabled="isThinking" />
    </div>
  </aside>
</template>