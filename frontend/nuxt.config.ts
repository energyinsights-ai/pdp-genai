// https://nuxt.com/docs/api/configuration/nuxt-config
// https://nuxt.com/docs/api/configuration/nuxt-config


import { definePreset } from '@primevue/themes';
import Aura from '@primevue/themes/aura';

const ddeTheme = definePreset(Aura, {
  semantic: {
    primary: {
      "50": "#e8e9ec",
      "100": "#d1d3da",
      "200": "#a3a6b5",
      "300": "#757a8f",
      "400": "#474d6a",
      "500": "#192145",
      "600": "#141a37",
      "700": "#0f1429",
      "800": "#0a0d1c",
      "900": "#05070e"
    }
},
components: {
  menubar:{
    colorScheme:{
      light:{
        root:{
          background: '#383c41',
          item:{
            color:'white'
          }
        },
        },
        dark:{
          root:{
            background: '#383c41',
            item:{
              color:'white'
            }
          },
          }
      }
    },
    selectbutton:{
      colorScheme:{
        light:{
          root:{
            background: '{primary.color}',
            item:{
              color:'white'
            }
          },
          }
        }
      },
      divider:{
        colorScheme:{
          light:{
            root:{
              border:{
                color: '{primary.color}'
              }
            },
            }
          }
        },
}
});
export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  ssr:false,
  devtools: { enabled: true },
  modules: [
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss',
    '@primevue/nuxt-module',
  ],
  plugins: [
    '~/plugins/chart.js',
    '~/plugins/primevue.js'
  ],
  runtimeConfig: {
    public: {
      apiBase: process.env.FLASK_BASE_URL || 'http://localhost:5000'
    }
  },
  primevue: {
    components: {
      include: ['Button', 'InputText', 'Textarea', 'Toast', 'Avatar', 'Menu', 'Menubar', 'Dialog', 'Message', 'DataTable', 'Column']
    },
    options: {
      theme: {
        preset: ddeTheme
      },
    },
  },
  css: [
    'primeicons/primeicons.css',
  ],
  // Remove the server configuration if present
})