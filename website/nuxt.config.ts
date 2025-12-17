// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  ssr: false,
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss', '@nuxt/content'],
  css: ['./app/assets/css/main.css'],
  content: {
    highlight: {
      theme: 'github-dark'
    }
  },
  app: {
    head: {
      title: 'Rift Operation Tools',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'The tools used by the Rift Operation group for making interactive and immersive experiences.' }
      ],
      link: [{ rel: 'icon', type: 'image/png', href: '/favicon.png' }]
    }
  }
})
