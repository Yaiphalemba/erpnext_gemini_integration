<script setup>
import { computed } from 'vue'

const props = defineProps({ data: Array })

// Dynamically grab column headers from the first dictionary object
const columns = computed(() => {
  if (!props.data || props.data.length === 0) return []
  return Object.keys(props.data[0])
})
</script>

<template>
  <div class="overflow-x-auto rounded-xl border border-white/5 bg-slate-800/50 scrollbar-hide">
    <table class="w-full text-left text-sm text-slate-300">
      <thead class="bg-slate-900/50 text-xs uppercase text-slate-500 font-semibold tracking-wider">
        <tr>
          <th v-for="col in columns" :key="col" class="px-4 py-3 whitespace-nowrap">
            {{ col.replace(/_/g, ' ') }}
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-white/5">
        <tr v-for="(row, index) in data" :key="index" class="hover:bg-slate-700/30 transition-colors">
          <td v-for="col in columns" :key="col" class="px-4 py-3 whitespace-nowrap">
            {{ row[col] }}
          </td>
        </tr>
      </tbody>
    </table>
    
    <div v-if="data.length >= 100" class="p-2 text-center text-xs text-slate-500 bg-slate-900/30">
      Showing top 100 results. Please refine your prompt for more specificity.
    </div>
  </div>
</template>