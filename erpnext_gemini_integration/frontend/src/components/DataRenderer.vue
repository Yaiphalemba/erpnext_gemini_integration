<script setup>
import { defineProps } from 'vue'
// Import your custom chart/table components
import SleekNumberCard from './charts/SleekNumberCard.vue'
import SleekBarChart from './charts/SleekBarChart.vue'
import MinimalTable from './charts/MinimalTable.vue'

const props = defineProps({
  type: String, // 'number_card', 'chart', 'table'
  data: Array,
  rawSql: String
})

const pinToDashboard = async () => {
  // Triggers the Frappe backend whitelist function we mapped out earlier
  console.log("Pinning query to dashboard:", props.rawSql)
  // frappe.call(...)
}
</script>

<template>
  <div class="relative group bg-slate-800/50 rounded-xl p-1 border border-white/5">
    
    <button @click="pinToDashboard" 
            class="absolute top-2 right-2 p-1.5 bg-slate-700 hover:bg-orange-500 text-slate-300 hover:text-white rounded-md opacity-0 group-hover:opacity-100 transition-all z-10"
            title="Pin to Dashboard">
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path></svg>
    </button>

    <SleekNumberCard v-if="type === 'number_card'" :data="data" />
    <SleekBarChart v-else-if="type === 'chart'" :data="data" />
    <MinimalTable v-else-if="type === 'table'" :data="data" />
    
  </div>
</template>