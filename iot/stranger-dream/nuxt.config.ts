export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss'],
  runtimeConfig: {
    public: {
      isDev: process.env.NODE_ENV !== 'production',
      defaultWsUrl: 'ws://192.168.10.7:8002/ws'
    }
  },
  app: {
      head: {
       link: [
         { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700;900&family=Cinzel:wght@400;700;900&display=swap' }
       ]
    }
  }
})
