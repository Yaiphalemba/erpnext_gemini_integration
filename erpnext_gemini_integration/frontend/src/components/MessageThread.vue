<script setup>
import { defineProps } from 'vue'
import DataRenderer from './DataRenderer.vue' // Remember we mapped this out earlier!

const props = defineProps({
  messages: Array,
  isThinking: Boolean
})
</script>

<template>
  <div class="flex flex-col space-y-4">
    <div v-for="(msg, index) in messages" :key="index"
         :class="['max-w-[85%] rounded-2xl p-4', 
            msg.role === 'user' 
              ? 'self-end bg-slate-800 text-slate-200 rounded-tr-sm' 
              : 'self-start bg-transparent text-slate-300 border border-white/5'
         ]">
      
      <p class="text-sm leading-relaxed whitespace-pre-wrap">{{ msg.text }}</p>

      <DataRenderer 
        v-if="msg.render_type && msg.render_type !== 'text'" 
        :type="msg.render_type" 
        :data="msg.data" 
        :rawSql="msg.raw_sql" 
        class="mt-4"
      />
    </div>

    <div v-if="isThinking" class="self-start max-w-[85%] p-4 text-slate-500 flex space-x-2">
      <div class="w-2 h-2 bg-orange-500 rounded-full animate-bounce"></div>
      <div class="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
      <div class="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
    </div>
  </div>
</template>