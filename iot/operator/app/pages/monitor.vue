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

const { selectedWebcams, webcamRotations, webcamFilters } = useRiftState()
const router = useRouter()

onMounted(() => {
  if (Object.keys(selectedWebcams.value).length === 0) {
    router.push('/config')
  }
})
</script>
