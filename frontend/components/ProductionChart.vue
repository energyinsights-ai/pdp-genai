<template>
  <div class="production-chart-container" style="height: 400px;">
    <Line 
      v-if="chartStore.chartData.datasets.length > 0" 
      :data="chartStore.chartData" 
      :options="chartStore.chartOptions"
    />
  </div>
</template>

<script setup lang="ts">
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, TimeScale } from 'chart.js'
import 'chartjs-adapter-date-fns'
import { useChartStore } from '~/stores/chartStore'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, TimeScale)

const chartStore = useChartStore()
</script>

<style scoped>
.production-chart-container {
  position: relative;
  height: 400px;
  width: 100%;
}
</style>