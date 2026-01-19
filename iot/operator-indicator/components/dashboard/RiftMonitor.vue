<script setup lang="ts">
import type { OperatorStatus } from '~/types/status'

const props = defineProps<{
  status: OperatorStatus | null
}>()

// Calculate progress percentage based on fragments collected
const progressPercentage = computed(() => {
  const count = props.status?.rift_part_count || 0
  return Math.round((count / 6) * 100)
})

const progressWidth = computed(() => {
  return `${progressPercentage.value}%`
})

const stageText = computed(() => {
  const count = props.status?.rift_part_count || 0
  if (count === 0) return 'Étape 1/3'
  if (count === 2) return 'Étape 2/3'
  if (count === 4) return 'Étape 3/3'
  if (count >= 6) return 'Complété'
  return 'Étape 1/3'
})

// SVG gradient offset (0 to 1) - fills from LEFT to RIGHT
const gradientOffset = computed(() => {
  return (progressPercentage.value / 100).toFixed(2)
})
</script>

<template>
  <div class="col-span-9 row-span-6 border border-[#00FFC2]/30 rounded-xl p-5 flex flex-col bg-[#0a0f11]">
    <div class="flex justify-between items-end mb-2">
      <div>
        <h2 class="text-sm font-semibold uppercase tracking-wider text-[#00FFC2] font-orbitron">Moniteur de faille</h2>
        <div class="text-white/60 text-xs mt-1 font-light font-inter">{{ stageText }}</div>
      </div>
      <span class="text-[#00FFC2] font-mono text-xl">{{ progressPercentage }}%</span>
    </div>
    
    <!-- Progress Bar -->
    <div class="w-full h-2 bg-gray-800 rounded-full mb-6 overflow-hidden border border-gray-700">
      <div class="h-full bg-[#00FFC2] shadow-[0_0_10px_#00FFC2] transition-all duration-500" :style="{ width: progressWidth }"></div>
    </div>

    <!-- SVG Burst Area -->
    <div class="flex-1 border border-gray-700/50 bg-gradient-to-b from-gray-900 to-black rounded-lg relative flex items-center justify-center overflow-hidden p-8">
      <!-- Rift Burst SVG -->
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 373 249" class="w-full h-full" preserveAspectRatio="xMidYMid meet">
        <defs>
          <!-- Gradient fills from LEFT to RIGHT with pink -->
          <linearGradient id="paint0_linear_progress" x1="0" y1="124.309" x2="372.935" y2="124.309" gradientUnits="userSpaceOnUse">
            <stop stop-color="#FF00CF"/>
            <stop :offset="gradientOffset" stop-color="#FF00CF"/>
            <stop :offset="gradientOffset" stop-color="#00FFC4"/>
            <stop offset="1" stop-color="#00FFC4"/>
          </linearGradient>
        </defs>
        
        <path 
          d="M292.576 221.581L260.574 187.563L235.713 185.254L227.162 196.814L193.216 168.977L179.749 187.411L172.89 183.837L163.668 186.146L152.053 204.282L153.73 188.637L146.223 190.52L137.679 201.082L114.663 216.627L61.207 248.618L99.5804 196.837L63.562 193.271C63.562 193.271 104.115 172.505 105.281 171.057C106.447 169.601 64.8271 165.753 64.8271 165.753L54.9346 166.172L44.6915 157.348L0 148.638L12.8953 139.28L14.0385 131.537L73.0734 113.835L72.0369 104.34L85.7934 99.8588L19.6783 27.2889L125.92 76.0981L117.102 10.4629L184.223 60.7886L194.809 40.7391L238.312 61.5125L322.916 0L300.921 65.399L303.863 70.9467L293.742 89.0758L312.3 93.0842L305.341 100.956L363.408 115.374L338.121 119.146L337.328 125.486L372.935 132.627L362.433 145.14L340.994 150.23C340.994 150.23 367.067 175.683 367.425 176.064C368.553 177.268 314.998 185.399 314.998 185.399L342.922 227.814L317.657 218.997L284.215 184.332" 
          fill="url(#paint0_linear_progress)"
          class="transition-all duration-700"
        />
      </svg>
      
      <!-- Grid overlay -->
      <div class="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:20px_20px] pointer-events-none"></div>
    </div>
  </div>
</template>

<style scoped>
.font-inter {
  font-family: 'Inter', sans-serif;
}

.font-orbitron {
  font-family: 'Orbitron', sans-serif;
}
</style>
