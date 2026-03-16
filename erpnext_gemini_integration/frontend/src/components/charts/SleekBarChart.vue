<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const props = defineProps({ data: Array })

// The AI gives us a list of dicts. We need to split it into Labels (X) and Data (Y).
// We assume the first column is the label (e.g., 'project_name') and the second is the value (e.g., 'total_cost').
const chartData = computed(() => {
  if (!props.data || props.data.length === 0) return { labels: [], datasets: [] }
  
  const keys = Object.keys(props.data[0])
  const labelKey = keys[0] 
  const valueKey = keys[1] 

  return {
    labels: props.data.map(row => row[labelKey]),
    datasets: [{
      label: valueKey.replace(/_/g, ' ').toUpperCase(),
      data: props.data.map(row => row[valueKey]),
      backgroundColor: '#f97316', // Tailwind orange-500
      borderRadius: 4, // Rounded bars look modern
      borderSkipped: false
    }]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } }, // Hide legend for minimalism
  scales: {
    x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
    y: { grid: { color: '#334155', borderDash: [5, 5] }, ticks: { color: '#94a3b8' } }
  }
}
</script>

<template>
  <div class="h-64 p-4 bg-slate-800/80 rounded-xl border border-white/5">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>