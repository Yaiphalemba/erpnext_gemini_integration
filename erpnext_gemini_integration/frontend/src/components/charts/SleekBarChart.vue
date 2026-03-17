<script setup>
import { defineProps, computed } from 'vue'

const props = defineProps({ data: Array })

const chartData = computed(() => {
  if (!props.data || props.data.length < 1) return { rows: [], max: 0 }
  
  const keys = Object.keys(props.data[0])
  
  // Smart column detection: Find which column holds the numbers
  const isNum = (val) => !isNaN(parseFloat(val)) && isFinite(val)
  const valKey = isNum(props.data[0][keys[0]]) ? keys[0] : keys[1]
  const labelKey = valKey === keys[0] ? keys[1] : keys[0]
  
  const rows = props.data.map(row => ({
    label: String(row[labelKey] || 'Unknown').replace(/_/g, ' '),
    value: Number(row[valKey] || 0)
  }))
  
  const max = Math.max(...rows.map(r => r.value)) || 1
  return { rows, max }
})
</script>