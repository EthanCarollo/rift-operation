<template>
  <div class="h-full w-full flex flex-col overflow-hidden relative">
    <!-- Main Content -->
    <div class="flex-1 overflow-hidden relative bg-black">
       <WebcamGrid 
         mode="view"
         :initial-selected="selectedWebcams"
         :initial-rotations="webcamRotations"
         :initial-filters="webcamFilters"
       />
       <!-- Overlay Lines for "Screen" effect -->
       <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%),linear-gradient(90deg,rgba(255,0,0,0.03),rgba(0,255,0,0.01),rgba(0,0,255,0.03))] z-10 bg-[length:100%_4px,6px_100%]"></div>
       
       <!-- Sector Indicator -->
       <div class="absolute top-4 right-4 z-20 px-4 py-2 bg-cyan-500/10 backdrop-blur-sm border border-cyan-500/30 rounded">
         <div class="flex items-center gap-2">
           <div class="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
           <span class="text-cyan-400 font-mono text-sm font-bold uppercase tracking-wider">{{ currentSector }}</span>
         </div>
       </div>
    </div>

    <!-- Hover Controls -->
    <div class="absolute bottom-4 right-4 z-50 opacity-0 hover:opacity-100 transition-opacity duration-500">
       <NuxtLink 
         to="/config" 
         class="px-3 py-1 bg-black/50 backdrop-blur text-xs font-bold uppercase text-white hover:bg-black/80 border border-white/20 rounded"
       >
         Return to Config
       </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRiftState } from '~/composables/useRiftState'
import { useRouter } from '#app'
import { onMounted } from 'vue'

const { selectedWebcams, webcamRotations, webcamFilters, appMode } = useRiftState()
const router = useRouter()

// Display sector based on appMode
const currentSector = computed(() => {
  if (!appMode.value) return 'NO CONFIG'
  return appMode.value === 'Dream' ? 'RÊVE' : 'CAUCHEMAR'
})

onMounted(() => {
  if (Object.keys(selectedWebcams.value).length === 0) {
    router.push('/config')
  }
})
</script>
