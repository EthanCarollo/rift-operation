<template>
  <div class="relative w-screen h-screen overflow-hidden font-cartoon">
    <!-- Background -->
    <div class="absolute inset-0 z-0">
       <img src="/images/banquise.png" alt="Banquise" class="w-full h-full object-cover object-center" />
    </div>
    
    <!-- Content -->
    <div class="relative z-10 h-full p-8 flex flex-col items-center">
      <h1 class="text-6xl md:text-8xl text-slate-100 mt-8 drop-shadow-[0_4px_4px_rgba(44,62,80,1)] tracking-wide">
        Stranger Dream
      </h1>
      
      <!-- Status Indicator -->
      <div 
        class="absolute top-8 right-8 bg-white/90 px-4 py-2 rounded-full flex items-center gap-2 shadow-lg backdrop-blur-sm"
      >
        <div 
          class="w-3 h-3 rounded-full shadow-md transition-all duration-300"
          :class="isConnected ? 'bg-green-500 shadow-green-400' : 'bg-red-500 shadow-red-400'"
        ></div>
        <span class="text-xs font-bold text-gray-700 font-sans tracking-wide">
          {{ isConnected ? 'ONLINE' : 'CONNECTING...' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useStrangerSocket } from '~/composables/useStrangerSocket'

const { isConnected } = useStrangerSocket()
</script>
