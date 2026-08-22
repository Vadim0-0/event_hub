import i18nOptions from './i18n.options'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },

  app: {
    head: {
      title: 'Event Hub',
      titleTemplate: '%s | Event Hub',
      link: [
        { rel: 'icon', type: 'image/svg', href: '/favicon.svg' },
      ],
      htmlAttrs: {
        lang: 'en',
      },
    },
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
      googleMapsApiKey: process.env.NUXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
      geoapifyApiKey: process.env.NUXT_PUBLIC_GEOAPIFY_API_KEY || '',
    },
  },

  css: [
    '~/assets/styles/base/fonts.css',
    '~/assets/styles/base/reset.css',
    '~/assets/styles/base/tailwind.css',
    '~/assets/styles/main.scss',
  ],

  components: [
    {
      path: '~/components'
    },
    {
      path: '~/components/ui'
    },
  ],

  modules: [
    '@nuxt/image',
    '@nuxt/ui',
    '@nuxt/test-utils',
    '@nuxtjs/i18n',
    // '@nuxtjs/ionic',
    // '@nuxtjs/ngrok',
    '@pinia/nuxt',
    '@vee-validate/nuxt',
    '@vueuse/nuxt',
    'dayjs-nuxt',
    // '@nuxtjs/eslint-module',
    'lenis/nuxt',
  ],
  pinia: {
    storesDirs: ['stores/**'],
  },
  imports: {
    dirs: ['composables/**'],
  },
  ui: {
    input: {
      defaultVariants: {
        variant: 'none',
      },
    },
  },

  // Avoid clash with nginx `/api/` → FastAPI proxy
  icon: {
    localApiEndpoint: '/_nuxt_icon',
  },

  i18n: i18nOptions,
})