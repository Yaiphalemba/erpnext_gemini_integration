<script setup>
import { defineProps, computed } from 'vue'
import SleekNumberCard from './charts/SleekNumberCard.vue'
import SleekBarChart from './charts/SleekBarChart.vue'
import MinimalTable from './charts/MinimalTable.vue'

const props = defineProps({
  renderType: { type: String, default: 'text' },
  data: { type: Array, default: () => [] }
})

const currentComponent = computed(() => {
  switch (props.renderType) {
    case 'number_card': return SleekNumberCard
    case 'chart': return SleekBarChart
    case 'table': return MinimalTable
    default: return null
  }
})
</script>

<template>
  <div v-if="currentComponent" class="mt-4 w-full">
    
    <div v-if="!data || data.length === 0" class="bg-slate-800/40 border border-slate-700/50 rounded-xl p-6 flex flex-col items-center justify-center text-center space-y-2">
      <div class="p-3 bg-slate-800/80 rounded-full shadow-inner mb-1">
        <svg class="w-6 h-6 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
      </div>
      <span class="text-sm font-medium text-slate-300">Zero records found</span>
      <span class="text-xs text-slate-500 max-w-[80%]">The AI wrote a flawless query, but the database came up empty for those specific conditions.</span>
    </div>

    <component v-else :is="currentComponent" :data="data" />
    
  </div>
</template>