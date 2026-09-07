import i18nOptions from './i18n.options'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },

  sourcemap: {
    server: false,
    client: false,
  },

  app: {
    head: {
      title: 'Event Hub',
      titleTemplate: '%s | Event Hub',
      link: [
        { rel: 'icon', type: 'image/svg', href: '/favicon.svg' },
        { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' },
      ],
      meta: [
        { name: 'theme-color', content: '#FAFAFA' },
        { name: 'mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-title', content: 'Event Hub' },
        { name: 'apple-mobile-web-app-status-bar-style', content: 'default' },
        {
          name: 'viewport',
          content: 'width=device-width, initial-scale=1, viewport-fit=cover',
        },
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
    //'@nuxt/test-utils',
    '@nuxtjs/i18n',
    // '@nuxtjs/ionic',
    // '@nuxtjs/ngrok',
    '@pinia/nuxt',
    '@vee-validate/nuxt',
    '@vueuse/nuxt',
    'dayjs-nuxt',
    // '@nuxtjs/eslint-module',
    'lenis/nuxt',
    '@vite-pwa/nuxt',
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

  // PWA
  pwa: {
    registerType: 'autoUpdate',
    registerWebManifestInRouteRules: true,
    manifest: {
      name: 'Event Hub',
      short_name: 'Event Hub',
      description: 'Event management platform',
      theme_color: '#FAFAFA',
      background_color: '#FAFAFA',
      display: 'standalone',
      scope: '/',
      id: '/',
      start_url: '/?source=pwa',
      icons: [
        { src: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' },
        { src: '/pwa-192x192.png', sizes: '192x192', type: 'image/png' },
        { src: '/pwa-512x512.png', sizes: '512x512', type: 'image/png' },
        { src: '/pwa-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
      ],
    },
    includeAssets: [
      'favicon.svg',
      'apple-touch-icon.png',
      'pwa-192x192.png',
      'pwa-512x512.png',
      'push-sw.js',
    ],
    workbox: {
      importScripts: ['/push-sw.js'],
      mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
      navigateFallback: '/',
      cleanupOutdatedCaches: true,
      clientsClaim: true,
      skipWaiting: true,
      globPatterns: ['**/*.{js,css,html,png,svg,ico,woff,woff2}'],
      runtimeCaching: [
        {
          urlPattern: /^https?:\/\/.*\/api\/.*/i,
          handler: 'NetworkOnly',
        },
      ],
    },
    client: {
      installPrompt: true,
    },
    devOptions: {
      enabled: process.env.NODE_ENV !== 'production',
      type: 'module',
    },
  },

  // Avoid clash with nginx `/api/` → FastAPI proxy
  icon: {
    localApiEndpoint: '/_nuxt_icon',
    serverBundle: {
      collections: [
        'akar-icons',
        'ant-design',
        'bi',
        'bitcoin-icons',
        'boxicons',
        'carbon',
        'ep',
        'eva',
        'fe',
        'fluent',
        'fontisto',
        'ic',
        'icon-park-outline',
        'ion',
        'line-md',
        'lsicon',
        'lucide',
        'mage',
        'material-symbols',
        'material-symbols-light',
        'mdi',
        'mingcute',
        'mynaui',
        'ri',
        'solar',
        'streamline',
        'tabler',
        'weui',
      ],
      // Keep @iconify/json installed, but don't inline JSON into Nitro bundle.
      externalizeIconsJson: true,
    },
    clientBundle: {
      scan: true,
    },
  },

  vite: {
    build: {
      reportCompressedSize: false,
    },
  },

  nitro: {
    minify: false,
  },

  i18n: i18nOptions,

  dayjs: {
    locales: ['en', 'ru'],
    defaultLocale: 'en',
  },
})