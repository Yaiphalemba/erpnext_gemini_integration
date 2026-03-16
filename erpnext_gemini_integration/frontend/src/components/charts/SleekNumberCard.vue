<script setup>
import { computed } from 'vue'

const props = defineProps({ data: Array })

// Safely extract the first value of the first row
const extractedNumber = computed(() => {
  if (!props.data || props.data.length === 0) return 0
  const firstRow = props.data[0]
  const firstKey = Object.keys(firstRow)[0]
  return firstRow[firstKey]
})

// Optional: Format numbers nicely (e.g., 1000000 -> 1M, or $1,000)
const formattedNumber = computed(() => {
  return new Intl.NumberFormat('en-IN', { notation: "compact" }).format(extractedNumber.value)
})
</script>

<template>
  <div class="flex flex-col items-start justify-center p-6 bg-slate-800/80 rounded-xl border border-white/5 shadow-inner">
    <span class="text-xs font-semibold tracking-widest text-slate-500 uppercase mb-2">Total Count</span>
    <span class="text-5xl font-light text-orange-400 tracking-tight">
      {{ formattedNumber }}
    </span>
  </div>
</template>