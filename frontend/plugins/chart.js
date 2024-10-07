import { Chart, registerables } from 'chart.js'
import { DateAdapter } from 'chartjs-adapter-date-fns'
import { enUS } from 'date-fns/locale'

Chart.register(...registerables)
Chart.register(DateAdapter)
Chart.defaults.locale = enUS