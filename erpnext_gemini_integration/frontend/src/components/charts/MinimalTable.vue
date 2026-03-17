<script setup>
import { defineProps, computed } from 'vue'

const props = defineProps({ data: Array })

const headers = computed(() => {
  if (!props.data || !props.data.length) return []
  return Object.keys(props.data[0])
})
</script>

<template>
  <div class="w-full overflow-x-auto rounded-xl border border-slate-700/50 bg-slate-800/30 scrollbar-hide">
    <table class="w-full text-left border-collapse">
      <thead>
        <tr class="bg-slate-800/80 border-b border-slate-700/50">
          <th v-for="header in headers" :key="header" class="py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider whitespace-nowrap">
            {{ header.replace(/_/g, ' ') }}
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-700/50">
        <tr v-for="(row, idx) in data" :key="idx" class="hover:bg-slate-700/20 transition-colors">
          <td v-for="header in headers" :key="header" class="py-3 px-4 text-sm text-slate-300 whitespace-nowrap">
            {{ row[header] }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>