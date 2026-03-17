<script setup>
import { defineProps, computed } from 'vue'

const props = defineProps({ data: Array })

const cardData = computed(() => {
  if (!props.data || !props.data.length) return { label: 'Metric', value: 'N/A' }
  const row = props.data[0]
  const key = Object.keys(row)[0]
  const val = row[key]
  
  return {
    label: key.replace(/_/g, ' '), // Clean up SQL aliases like "total_sales" -> "total sales"
    value: typeof val === 'number' ? val.toLocaleString() : val
  }
})
</script>

<template>
  <div class="bg-slate-800/40 border border-slate-700/50 rounded-xl p-6 flex flex-col items-center justify-center relative overflow-hidden group">
    <div class="absolute -top-10 -right-10 w-32 h-32 bg-orange-500/10 rounded-full blur-3xl group-hover:bg-orange-500/20 transition-all duration-500"></div>
    
    <span class="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2 z-10">{{ cardData.label }}</span>
    <span class="text-4xl font-black bg-gradient-to-br from-white to-slate-400 bg-clip-text text-transparent z-10">
      {{ cardData.value }}
    </span>
  </div>
</template>