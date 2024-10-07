import { defineStore } from 'pinia'
import type { ChartData, ChartOptions } from 'chart.js'

interface WellData {
  dates: string[];
  oil_production: number[];
  gas_production: number[];
  oil_forecast: number[];
  gas_forecast: number[];
  forecast_dates: string[];
}

export const useChartStore = defineStore('chart', {
  state: () => ({
    rawData: null as WellData | null,
    originalForecast: { oil: [] as number[], gas: [] as number[] },
    oilAdjustment: 0,
    gasAdjustment: 0,
    chartOptions: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: 'time',
          time: {
            unit: 'month',
            displayFormats: {
              month: 'MMM yyyy'
            }
          },
          title: {
            display: true,
            text: 'Date'
          }
        },
        y: {
          title: {
            display: true,
            text: 'Production'
          },
          beginAtZero: true
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: (context: any) => {
              const label = context.dataset.label || ''
              const value = context.parsed.y
              return `${label}: ${value.toLocaleString()}`
            }
          }
        },
        legend: {
          display: true
        }
      }
    } as ChartOptions<'line'>
  }),
  getters: {
    currentForecast(): { oil: number[], gas: number[] } {
      return {
        oil: this.originalForecast.oil.map(value => value * (1 + this.oilAdjustment / 100)),
        gas: this.originalForecast.gas.map(value => value * (1 + this.gasAdjustment / 100))
      }
    },
    chartData(): ChartData<'line'> {
      if (!this.rawData) return { datasets: [] }

      const { dates, oil_production, gas_production, forecast_dates } = this.rawData
      const { oil: currentOilForecast, gas: currentGasForecast } = this.currentForecast

      return {
        datasets: [
          {
            label: 'Oil Production',
            data: oil_production.map((value, index) => ({ x: new Date(dates[index]).getTime(), y: value })),
            borderColor: 'rgba(0, 128, 0, 1)',
            backgroundColor: 'rgba(0, 128, 0, 0.2)',
            pointRadius: 4,
            pointHoverRadius: 6,
          },
          {
            label: 'Gas Production',
            data: gas_production.map((value, index) => ({ x: new Date(dates[index]).getTime(), y: value })),
            borderColor: 'rgba(255, 0, 0, 1)',
            backgroundColor: 'rgba(255, 0, 0, 0.2)',
            pointRadius: 4,
            pointHoverRadius: 6,
          },
          {
            label: 'Oil Forecast',
            data: currentOilForecast.map((value, index) => ({ x: new Date(forecast_dates[index]).getTime(), y: value })),
            borderColor: 'rgba(0, 128, 0, 0.5)',
            backgroundColor: 'rgba(0, 128, 0, 0.1)',
            borderDash: [5, 5],
            pointRadius: 3,
            pointHoverRadius: 5,
          },
          {
            label: 'Gas Forecast',
            data: currentGasForecast.map((value, index) => ({ x: new Date(forecast_dates[index]).getTime(), y: value })),
            borderColor: 'rgba(255, 0, 0, 0.5)',
            backgroundColor: 'rgba(255, 0, 0, 0.1)',
            borderDash: [5, 5],
            pointRadius: 3,
            pointHoverRadius: 5,
          }
        ]
      }
    }
  },
  actions: {
    setRawData(data: WellData) {
      this.rawData = data
      this.originalForecast = {
        oil: data.oil_forecast,
        gas: data.gas_forecast
      }
    },
    updateChartOptions(newOptions: Partial<ChartOptions<'line'>>) {
      this.chartOptions = { 
        ...this.chartOptions, 
        ...newOptions,
        scales: {
          ...this.chartOptions.scales,
          ...(newOptions.scales || {}),
          x: {
            ...(this.chartOptions.scales?.x as any),
            ...(newOptions.scales?.x || {}),
            type: 'time',
            time: {
              ...(this.chartOptions.scales?.x as any)?.time,
              ...(newOptions.scales?.x as any)?.time
            }
          }
        }
      }
    },
    setAdjustments(oil: number, gas: number) {
      this.oilAdjustment = oil
      this.gasAdjustment = gas
    }
  }
})