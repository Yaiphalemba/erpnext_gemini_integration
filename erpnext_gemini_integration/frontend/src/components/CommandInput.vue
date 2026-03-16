<script setup>
import { ref, defineEmits, defineProps } from 'vue'

const emit = defineEmits(['submit'])
const props = defineProps({ disabled: Boolean })

const userInput = ref('')
const showMentionPopover = ref(false)

const handleInput = (e) => {
  const text = e.target.value
  const cursorPosition = e.target.selectionStart
  const textBeforeCursor = text.slice(0, cursorPosition)
  
  // Basic detection for opening the @ menu
  if (textBeforeCursor.match(/@[a-zA-Z0-9-]*$/)) {
    showMentionPopover.value = true
  } else {
    showMentionPopover.value = false
  }
}

const triggerSend = () => {
  if (!userInput.value.trim() || props.disabled) return
  
  emit('submit', userInput.value)
  userInput.value = ''
  showMentionPopover.value = false
}
</script>

<template>
  <div class="relative w-full">
    <div v-if="showMentionPopover" 
         class="absolute bottom-full mb-2 left-0 w-full bg-slate-800 border border-slate-700 rounded-lg shadow-xl p-2 z-50">
      <div class="text-xs text-slate-400 font-semibold mb-1 px-2 uppercase tracking-wider">Quick Tag</div>
      <ul class="text-sm text-slate-300 space-y-1">
        <li class="p-2 hover:bg-slate-700 hover:text-orange-400 rounded transition-colors">
          <span class="font-mono text-orange-500 text-xs mr-2">PROJ</span> Type project ID
        </li>
        <li class="p-2 hover:bg-slate-700 hover:text-orange-400 rounded transition-colors">
          <span class="font-mono text-orange-500 text-xs mr-2">EMP</span> Type employee ID
        </li>
      </ul>
    </div>

    <div class="relative flex items-center">
      <textarea 
        v-model="userInput"
        @input="handleInput"
        @keydown.enter.prevent="triggerSend"
        :disabled="disabled"
        placeholder="Ask for a report, or type @ to link data..."
        class="w-full bg-slate-800/50 text-slate-200 rounded-xl py-3 pl-4 pr-12 focus:outline-none focus:ring-1 focus:ring-orange-500/50 border border-transparent focus:border-orange-500/30 resize-none h-[52px] overflow-hidden transition-all placeholder-slate-500 text-sm disabled:opacity-50"
        rows="1"
      ></textarea>
      
      <button 
        @click="triggerSend" 
        :disabled="disabled || !userInput.trim()"
        class="absolute right-2 p-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
        <svg class="w-4 h-4 transform rotate-90" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"></path>
        </svg>
      </button>
    </div>
  </div>
</template>