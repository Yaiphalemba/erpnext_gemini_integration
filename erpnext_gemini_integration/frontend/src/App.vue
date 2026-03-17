<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import AIChatDrawer from './components/AIChatDrawer.vue'

const isOpen = ref(false)
const toggleChat = () => isOpen.value = !isOpen.value

// The sweet Cmd+K / Ctrl+K shortcut
const handleGlobalKeydown = (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    toggleChat()
  }
}

onMounted(() => window.addEventListener('keydown', handleGlobalKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleGlobalKeydown))
</script>

<template>
  <div>
    <button 
      @click="toggleChat"
      class="fixed bottom-6 right-6 z-[9999] p-4 rounded-full bg-slate-800 text-orange-500 shadow-2xl border border-white/10 hover:bg-slate-700 hover:scale-110 hover:shadow-orange-500/30 transition-all duration-300 group"
      title="Open AI Analyst (Cmd+K)"
    >
      <svg class="w-6 h-6 group-hover:animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
      </svg>
    </button>

    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 translate-y-8 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-8 scale-95"
    >
      <AIChatDrawer v-if="isOpen" @close="toggleChat" />
    </Transition>
  </div>
</template>