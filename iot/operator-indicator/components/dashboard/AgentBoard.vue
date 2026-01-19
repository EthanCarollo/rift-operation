<script setup lang="ts">
import type { OperatorStatus } from '~/types/status'

const props = defineProps<{
  status: OperatorStatus | null
}>()

// Determine current layout based on mission state
const currentLayout = computed(() => {
  const status = props.status
  
  // Layout 4: After step 3
  if (status?.operator_launch_close_rift_step_3) {
    return 4
  }
  
  // Layout 3: After step 2
  if (status?.operator_launch_close_rift_step_2) {
    return 3
  }
  
  // Layout 2: After step 1
  if (status?.operator_launch_close_rift_step_1) {
    return 2
  }
  
  // Layout 1: After stranger becomes inactive (case 2 in MissionBriefing)
  if (status?.stranger_state === 'inactive') {
    return 1
  }
  
  // Layout 0: Default - before case 2
  return 0
})

// Agent positions based on layout
const agent1Position = computed(() => {
  switch (currentLayout.value) {
    case 0: return { top: '50%', left: '33%' } // Center-left (image 0)
    case 1: return { top: '65%', left: '33%' } // Lower center-left (image 1)
    case 2: return { top: '35%', left: '25%' } // Upper left (image 2)
    case 3:
    case 4: return { bottom: '15%', left: '30%' } // Bottom (images 3, 4)
    default: return { top: '50%', left: '33%' }
  }
})

const agent2Position = computed(() => {
  switch (currentLayout.value) {
    case 0: return { top: '50%', right: '33%' }
    case 1: return { top: '65%', right: '33%' }
    case 2: return { top: '35%', right: '25%' }
    case 3:
    case 4: return { bottom: '15%', right: '30%' }
    default: return { top: '50%', right: '33%' }
  }
})

// Health bars based on layout
const agent1Health = computed(() => {
  switch (currentLayout.value) {
    case 0: return { health: 100, energy: 100 } 
    case 1: return { health: 100, energy: 100 }
    case 2: return { health: 100, energy: 85 } 
    case 3: return { health: 99, energy: 72 }
    case 4: return { health: 27, energy: 35 } 
    default: return { health: 100, energy: 100 }
  }
})
const agent2Health = computed(() => {
  switch (currentLayout.value) {
    case 0: return { health: 100, energy: 100 } 
    case 1: return { health: 100, energy: 100 }
    case 2: return { health: 92, energy: 89 } 
    case 3: return { health: 92, energy: 67 } 
    case 4: return { health: 32, energy: 15 }
    default: return { health: 100, energy: 100 }
  }
})
</script>

<template>
  <div class="col-span-6 row-span-6 border border-[#00FFC2]/30 rounded-xl p-0 relative flex overflow-hidden bg-[#0a0f11]">
    <div class="absolute inset-x-0 top-0 h-14 bg-gradient-to-b from-[#00FFC2]/5 to-transparent pointer-events-none"></div>
    <h2 class="absolute top-4 left-5 text-sm font-semibold uppercase tracking-wider text-[#00FFC2] z-20 font-orbitron">Tableau de bord Agent</h2>

    <div class="flex w-full h-full pt-14">
      <!-- LEFT: MAP -->
      <div class="w-1/2 h-full border-r border-[#00FFF0]/20 relative bg-black/40">
        <div class="absolute top-2 left-4 text-[10px] text-gray-500 uppercase tracking-widest font-inter">Zone Rêve</div>
        <div class="absolute top-2 right-4 text-[10px] text-gray-500 uppercase tracking-widest font-inter">Zone Cauchemar</div>
        
        <!-- Rift Line SVG -->
        <div class="absolute inset-0 flex justify-center items-center">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 31 393" class="h-full w-auto opacity-80" preserveAspectRatio="xMidYMid meet">
            <defs>
              <linearGradient id="paint0_linear_rift" x1="15.5484" y1="-67.3898" x2="15.5484" y2="438.413" gradientUnits="userSpaceOnUse">
                <stop stop-opacity="0"/>
                <stop offset="0.5" stop-color="#00FFFF" stop-opacity="0.5"/>
                <stop offset="1" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <path d="M24.5178 0.319763L7.95925 76.2169L21.0683 94.8462L1.74902 120.375L29.3477 177.643L16.9282 237.671L3.1287 246.64L17.6182 278.379L15.5482 356.346L24.5179 397.055" stroke="url(#paint0_linear_rift)" stroke-width="3" fill="none" class="drop-shadow-[0_0_10px_rgba(0,255,255,0.5)]"/>
          </svg>
        </div>

        <!-- Agent Dot 1 (Pink) -->
        <div 
          class="absolute transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-1 group transition-all duration-1000 ease-in-out"
          :style="agent1Position"
        >
          <div class="relative w-10 h-10">
            <!-- Radar ping rings -->
            <div class="absolute inset-0 rounded-full border-2 border-pink-500 animate-radar-ping"></div>
            <div class="absolute inset-0 rounded-full border-2 border-pink-500 animate-radar-ping animation-delay-700"></div>
            <!-- Agent icon -->
            <div class="absolute inset-0 rounded-full border-2 border-pink-500 bg-pink-500/20 flex items-center justify-center shadow-[0_0_10px_rgba(236,72,153,0.5)]">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="url(#gradient-pink)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <defs>
                  <linearGradient id="gradient-pink" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#ec4899;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#f472b6;stop-opacity:1" />
                  </linearGradient>
                </defs>
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </div>
          </div>
          <span class="text-[9px] text-pink-400 uppercase tracking-wider group-hover:scale-110 transition-transform font-inter">Agent 1</span>
        </div>

        <!-- Agent Dot 2 (Cyan) -->
        <div 
          class="absolute transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-1 group transition-all duration-1000 ease-in-out"
          :style="agent2Position"
        >
          <div class="relative w-10 h-10">
            <!-- Radar ping rings -->
            <div class="absolute inset-0 rounded-full border-2 border-[#00FFF0] animate-radar-ping"></div>
            <div class="absolute inset-0 rounded-full border-2 border-[#00FFF0] animate-radar-ping animation-delay-700"></div>
            <!-- Agent icon -->
            <div class="absolute inset-0 rounded-full border-2 border-[#00FFF0] bg-[#00FFF0]/20 flex items-center justify-center shadow-[0_0_10px_rgba(0,255,240,0.5)]">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="url(#gradient-cyan)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <defs>
                  <linearGradient id="gradient-cyan" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#00FFF0;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#22d3ee;stop-opacity:1" />
                  </linearGradient>
                </defs>
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </div>
          </div>
          <span class="text-[9px] text-[#00FFF0] uppercase tracking-wider group-hover:scale-110 transition-transform font-inter">Agent 2</span>
        </div>
      </div>

      <!-- RIGHT: STATS -->
      <div class="w-1/2 h-full p-4 flex flex-col gap-4">
        
        <!-- Agent 1 Card -->
        <div class="border border-pink-500/30 bg-gradient-to-br from-pink-500/5 to-transparent rounded-lg p-3">
          <div class="flex items-start justify-between mb-2">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full border border-pink-500 flex items-center justify-center text-pink-500 bg-pink-900/10">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="url(#gradient-pink-card)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <defs>
                    <linearGradient id="gradient-pink-card" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style="stop-color:#ec4899;stop-opacity:1" />
                      <stop offset="100%" style="stop-color:#f472b6;stop-opacity:1" />
                    </linearGradient>
                  </defs>
                  <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
              </div>
              <div>
                <div class="text-pink-500 font-bold text-sm tracking-wide font-orbitron">Agent 1</div>
                <div class="text-[9px] text-gray-400 uppercase tracking-widest font-inter">Navigateur Onirique</div>
              </div>
            </div>
            <div class="flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-pink-500 animate-pulse"></span>
              <span class="text-[9px] text-pink-500 font-inter">En Mission</span>
            </div>
          </div>
          <!-- Bars -->
          <div class="space-y-2 mt-2">
            <div class="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-pink-500">
                <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
              </svg>
              <div class="h-1.5 flex-1 bg-gray-800 rounded-full overflow-hidden">
                <div class="h-full bg-pink-500 shadow-[0_0_5px_rgba(236,72,153,0.8)] transition-all duration-1000 ease-in-out" :style="{ width: `${agent1Health.health}%` }"></div>
              </div>
              <span class="text-[9px] text-gray-400 w-6 text-right font-mono">{{ agent1Health.health }}%</span>
            </div>
            <div class="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-pink-500">
                <path d="m13 2-2 2.5L9 7l3 3-2 2.5L8 15l3 3-2 2.5L7 23"/>
                <path d="M11 2 9 4.5 7 7l3 3-2 2.5L6 15l3 3-2 2.5L5 23"/>
              </svg>
              <div class="h-1.5 flex-1 bg-gray-800 rounded-full overflow-hidden">
                <div class="h-full bg-pink-400 shadow-[0_0_5px_rgba(244,114,182,0.8)] transition-all duration-1000 ease-in-out" :style="{ width: `${agent1Health.energy}%` }"></div>
              </div>
              <span class="text-[9px] text-gray-400 w-6 text-right font-mono">{{ agent1Health.energy }}%</span>
            </div>
          </div>
        </div>

        <!-- Agent 2 Card -->
        <div class="border border-[#00FFF0]/30 bg-gradient-to-br from-[#00FFF0]/5 to-transparent rounded-lg p-3">
          <div class="flex items-start justify-between mb-2">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full border border-[#00FFF0] flex items-center justify-center text-[#00FFF0] bg-[#00FFF0]/5">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="url(#gradient-cyan-card)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <defs>
                    <linearGradient id="gradient-cyan-card" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style="stop-color:#00FFF0;stop-opacity:1" />
                      <stop offset="100%" style="stop-color:#22d3ee;stop-opacity:1" />
                    </linearGradient>
                  </defs>
                  <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
              </div>
              <div>
                <div class="text-[#00FFF0] font-bold text-sm tracking-wide font-orbitron">Agent 2</div>
                <div class="text-[9px] text-gray-400 uppercase tracking-widest font-inter">Chasseur de Cauchemars</div>
              </div>
            </div>
            <div class="flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-[#00FFF0] animate-pulse"></span>
              <span class="text-[9px] text-[#00FFF0] font-inter">En Mission</span>
            </div>
          </div>
          <!-- Bars -->
          <div class="space-y-2 mt-2">
            <div class="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[#00FFF0]">
                <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
              </svg>
              <div class="h-1.5 flex-1 bg-gray-800 rounded-full overflow-hidden">
                <div class="h-full bg-[#00FFF0] shadow-[0_0_5px_rgba(0,255,240,0.8)] transition-all duration-1000 ease-in-out" :style="{ width: `${agent2Health.health}%` }"></div>
              </div>
              <span class="text-[9px] text-gray-400 w-6 text-right font-mono">{{ agent2Health.health }}%</span>
            </div>
            <div class="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[#00FFF0]">
                <path d="m13 2-2 2.5L9 7l3 3-2 2.5L8 15l3 3-2 2.5L7 23"/>
                <path d="M11 2 9 4.5 7 7l3 3-2 2.5L6 15l3 3-2 2.5L5 23"/>
              </svg>
              <div class="h-1.5 flex-1 bg-gray-800 rounded-full overflow-hidden">
                <div class="h-full bg-[#00FFF0]/70 shadow-[0_0_5px_rgba(0,255,240,0.6)] transition-all duration-1000 ease-in-out" :style="{ width: `${agent2Health.energy}%` }"></div>
              </div>
              <span class="text-[9px] text-gray-400 w-6 text-right font-mono">{{ agent2Health.energy }}%</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.font-orbitron {
  font-family: 'Orbitron', sans-serif;
}
.font-inter {
  font-family: 'Inter', sans-serif;
}

/* Radar ping animation (GPS-style) */
@keyframes radar-ping {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(2.5);
    opacity: 0;
  }
}

.animate-radar-ping {
  animation: radar-ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.animation-delay-700 {
  animation-delay: 0.7s;
}
</style>
