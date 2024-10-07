<template>
  <div class="min-h-screen flex flex-col bg-gradient-to-br from-gray-900 to-gray-800">
    <!-- Navigation Bar -->
    <nav class="bg-black text-white p-4">
      <div class="container mx-auto flex justify-between items-center">
        <div class="text-xl font-bold">WellForecast</div>
        <button @click="showHelp = true" class="text-white hover:text-gray-300 transition-colors duration-300" aria-label="Help">
          <i class="pi pi-question-circle text-xl"></i>
        </button>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="flex-grow py-4 sm:py-8">
      <div class="container mx-auto px-4 sm:px-6 max-w-7xl">
        <div class="mb-6 sm:mb-8 text-center">
          <h1 class="text-3xl sm:text-4xl font-bold mb-4 text-yellow-400 animate-fade-in">
            Well Production Forecast
          </h1>
          <div class="w-32 h-32 sm:w-48 sm:h-48 mx-auto mb-4 rounded-full overflow-hidden shadow-lg border-4 border-yellow-400">
            <!-- Placeholder for AI-generated oil art -->
            <div class="w-full h-full bg-gradient-to-br from-yellow-600 to-black animate-pulse"></div>
          </div>
        </div>
        
        <div class="flex flex-wrap -mx-2 sm:-mx-4">
          <div class="w-full lg:w-2/3 px-2 sm:px-4 mb-4 sm:mb-8">
            <div class="bg-gray-800 rounded-lg shadow-lg p-4 sm:p-6 transition-all duration-300 hover:shadow-xl h-full border border-yellow-400">
              <Select
                v-model="selectedWell"
                :options="wells"
                optionLabel="name"
                optionValue="code"
                placeholder="Select a well"
                class="w-full mb-4 sm:mb-6"
                @change="loadWellData"
                :loading="isLoading"
                aria-label="Select a well"
              />
              <div class="production-chart-container relative">
                <ProductionChart />
                <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-gray-800 bg-opacity-70">
                  <ProgressSpinner />
                </div>
              </div>
            </div>
          </div>
          <div class="w-full lg:w-1/3 px-2 sm:px-4 mb-4 sm:mb-8">
            <div class="bg-gray-800 rounded-lg shadow-lg p-4 sm:p-6 transition-all duration-300 hover:shadow-xl h-full flex flex-col border border-yellow-400">
              <h2 class="text-xl sm:text-2xl font-semibold mb-4 sm:mb-6 text-yellow-400">Forecast Tuning</h2>
              <div v-if="selectedWell" class="flex-grow">
                <div class="mb-4 sm:mb-6">
                  <h3 class="font-semibold text-gray-300 mb-2">Oil Forecast Adjustment</h3>
                  <Slider v-model="chartStore.oilAdjustment" :min="-100" :max="100" class="w-full mb-2" aria-label="Oil forecast adjustment" />
                  <span class="text-yellow-400 font-medium">{{ chartStore.oilAdjustment }}%</span>
                </div>
                <div class="mb-4 sm:mb-6">
                  <h3 class="font-semibold text-gray-300 mb-2">Gas Forecast Adjustment</h3>
                  <Slider v-model="chartStore.gasAdjustment" :min="-100" :max="100" class="w-full mb-2" aria-label="Gas forecast adjustment" />
                  <span class="text-yellow-400 font-medium">{{ chartStore.gasAdjustment }}%</span>
                </div>
              </div>
              <div v-else class="text-center text-gray-400 flex-grow">
                Please select a well to adjust the forecast.
              </div>
              <div class="flex justify-center mt-4 sm:mt-6">
                <Button 
                  label="Reset Forecast" 
                  @click="resetForecast" 
                  class="p-button-secondary bg-yellow-500 hover:bg-yellow-600 text-gray-900 font-semibold py-2 px-4 rounded transition-colors duration-300"
                  :disabled="!selectedWell"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="bg-black text-white py-4">
      <div class="container mx-auto text-center text-sm">
        <p>&copy; 2023 WellForecast. All rights reserved.</p>
      </div>
    </footer>

    <!-- Help Dialog -->
    <Dialog v-model:visible="showHelp" header="How to use WellForecast" :modal="true" :breakpoints="{'960px': '75vw', '640px': '90vw'}" :style="{width: '50vw'}">
      <p class="m-0 text-sm sm:text-base">
        1. Select a well from the dropdown menu.<br>
        2. View the production forecast chart.<br>
        3. Adjust the oil and gas forecasts using the sliders.<br>
        4. Click "Reset Forecast" to return to the original values.
      </p>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useRuntimeConfig } from '#app'
import { useChartStore } from '~/stores/chartStore'
import ProductionChart from '~/components/ProductionChart.vue'

const config = useRuntimeConfig()
const toast = useToast()
const chartStore = useChartStore()

const wells = ref([])
const selectedWell = ref(null)
const isLoading = ref(false)
const showHelp = ref(false)

onMounted(async () => {
  try {
    isLoading.value = true
    const response = await fetch(`${config.public.apiBase}/api/wells`)
    const data = await response.json()
    wells.value = data.map((well: string) => ({ name: well, code: well }))
  } catch (error) {
    console.error('Error loading wells:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load wells. Please try refreshing the page.', life: 5000 })
  } finally {
    isLoading.value = false
  }
})

const loadWellData = async () => {
  if (!selectedWell.value) return

  chartStore.setAdjustments(0, 0)

  try {
    isLoading.value = true
    const response = await fetch(`${config.public.apiBase}/api/well_data/${selectedWell.value}`)
    if (!response.ok) {
      throw new Error('An error occurred while fetching well data')
    }
    const data = await response.json()

    chartStore.setRawData(data)

    const allDates = [...data.dates, ...data.forecast_dates].map(d => new Date(d).getTime())
    const minDate = Math.min(...allDates)
    const maxDate = Math.max(...allDates)

    chartStore.updateChartOptions({
      scales: {
        x: {
          min: minDate,
          max: maxDate
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              let label = context.dataset.label || '';
              if (label) {
                label += ': ';
              }
              if (context.parsed.y !== null) {
                label += new Intl.NumberFormat('en-US', { style: 'decimal' }).format(context.parsed.y);
              }
              return label;
            }
          }
        }
      }
    })

  } catch (error: any) {
    console.error('Error loading well data:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load well data. Please try again or select a different well.', life: 5000 })
  } finally {
    isLoading.value = false
  }
}

const resetForecast = () => {
  chartStore.setAdjustments(0, 0)
  toast.add({ severity: 'info', summary: 'Info', detail: 'Forecast reset to original values', life: 3000 })
}
</script>

<style scoped>
.production-chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.animate-fade-in {
  animation: fadeIn 1s ease-in-out;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@media (min-width: 640px) {
  .production-chart-container {
    height: 400px;
  }
}

@media (min-width: 1024px) {
  .production-chart-container {
    height: 500px;
  }
}
</style>