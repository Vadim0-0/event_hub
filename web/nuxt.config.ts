import i18nOptions from './i18n.options'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },

  app: {
    head: {
      title: 'Event Hub',
      titleTemplate: '%s | Event Hub',
      htmlAttrs: {
        lang: 'en',
      },
    },
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
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
    }
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

  i18n: i18nOptions,
})