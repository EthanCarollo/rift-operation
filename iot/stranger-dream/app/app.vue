<template>
  <div class="relative w-screen h-screen overflow-hidden font-cartoon">
    <!-- Background -->
    <div class="absolute inset-0 z-0">
       <img src="/images/banquise_light.png" alt="Banquise" class="w-full h-full object-cover object-center" />
    </div>
    
    <!-- Content -->
    <div class="relative z-10 h-full flex flex-col items-center justify-center p-8 transition-all duration-500">
      
      <!-- Logo/Title (Always visible or maybe hidden when active? Request says "shows nothing" if inactive, implies showing title if inactive is base screen) -->
      <!-- Request says: "stranger_state : 'inactive' -> tu affiches rien du tout et reviens à l'écran de base" -->
      <!-- Let's assume "nothing" means no question, just the base screen (Title) -->
      
      <div v-if="strangerState === 'inactive'" class="transition-opacity duration-500">
          <h1 class="text-6xl md:text-8xl text-slate-700 mt-8 drop-shadow-sm tracking-wide opacity-80">
            Stranger Dream
          </h1>
      </div>

      <!-- Question Overlay -->
      <div v-else class="flex flex-col items-center justify-center text-center animate-fade-in-up">
        <div class="bg-white/90 backdrop-blur-md p-12 rounded-3xl shadow-xl max-w-4xl transform transition-all duration-500 hover:scale-105">
           <h2 class="text-5xl md:text-7xl text-slate-800 leading-tight">
             {{ currentQuestion }}
           </h2>
        </div>
      </div>
      
      <!-- Status Indicator -->
      <div 
        class="absolute top-8 right-8 bg-white/80 px-4 py-2 rounded-full flex items-center gap-2 shadow-sm backdrop-blur-sm"
      >
        <div 
          class="w-3 h-3 rounded-full shadow-sm transition-all duration-300"
          :class="isConnected ? 'bg-green-400' : 'bg-red-400'"
        ></div>
        <!-- Debug State -->
        <span class="text-xs font-bold text-gray-500 font-sans tracking-wide uppercase">
          {{ isConnected ? (strangerState !== 'inactive' ? strangerState : 'ONLINE') : 'CONNECTING...' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useStrangerSocket } from '~/composables/useStrangerSocket'
import { questions } from '~/config/questions'

const { isConnected, strangerState } = useStrangerSocket()

const currentQuestion = computed(() => {
    return questions[strangerState.value] || ''
})
</script>
