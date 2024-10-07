import { defineNuxtPlugin } from '#app'
import PrimeVue from 'primevue/config'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Toast from 'primevue/toast'
import ToastService from 'primevue/toastservice'
import Avatar from 'primevue/avatar'
import Menu from 'primevue/menu'
import Menubar from 'primevue/menubar'
import Tooltip from 'primevue/tooltip'
import Popover from 'primevue/popover'

export default defineNuxtPlugin((nuxtApp) => {
    nuxtApp.vueApp.use(PrimeVue, { ripple: true })
    nuxtApp.vueApp.use(ToastService)
    nuxtApp.vueApp.component('Button', Button)
    nuxtApp.vueApp.component('InputText', InputText)
    nuxtApp.vueApp.component('Toast', Toast)
    nuxtApp.vueApp.component('Avatar', Avatar)
    nuxtApp.vueApp.component('Menu', Menu)
    nuxtApp.vueApp.component('Menubar', Menubar)
    nuxtApp.vueApp.directive('tooltip', Tooltip)
    nuxtApp.vueApp.component('Popover', Popover)
})