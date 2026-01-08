// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  app: {
    head: {
      title: 'MIDI Visualizer',
      meta: [
        { name: 'description', content: 'Visualize MIDI files in a sequencer-style piano roll' }
      ]
    }
  },
  css: ['~/assets/main.css']
})
