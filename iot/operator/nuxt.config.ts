// https://nuxt.com/docs/api/configuration/nuxt-config
export default {
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss'],
  runtimeConfig: {
    public: {
      // 1. Local WPA
      wsUrl: 'ws://192.168.10.7:8000/ws',

      // 2. PRODUCTION (Online Server)
      // wsUrl: 'wss://server.riftoperation.ethan-folio.fr/ws',
    }
  },
  app: {
    head: {
      link: [
        { rel: 'icon', type: 'image/png', href: '/favicon.png' }
      ]
    }
  }
}
