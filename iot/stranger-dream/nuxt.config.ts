export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss'],
  app: {
    head: {
       link: [
         { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Fredoka+One&display=swap' }
       ]
    }
  }
})
