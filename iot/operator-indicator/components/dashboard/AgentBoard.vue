<script setup lang="ts">
const props = defineProps<{
  status: any
}>()
</script>

<template>
  <div class="col-span-6 row-span-6 border border-[#00FFC2]/30 rounded-xl p-0 relative flex overflow-hidden bg-[#0a0f11]">
    <div class="absolute inset-x-0 top-0 h-14 bg-gradient-to-b from-[#00FFC2]/5 to-transparent pointer-events-none"></div>
    <h2 class="absolute top-4 left-5 text-sm font-semibold uppercase tracking-wider text-[#00FFC2] z-20 font-inter">Tableau de bord Agent</h2>

    <div class="flex w-full h-full pt-14">
      <!-- LEFT: MAP -->
      <div class="w-1/2 h-full border-r border-[#00FFF0]/20 relative bg-black/40">
        <div class="absolute top-2 left-4 text-[10px] text-gray-500 uppercase tracking-widest font-inter">Zone Rêve</div>
        <div class="absolute top-2 right-4 text-[10px] text-gray-500 uppercase tracking-widest font-inter">Zone Cauchemar</div>
        
        <!-- Rift Line -->
        <div class="absolute inset-0 flex justify-center">
          <div class="w-1 h-full bg-[#00FFF0]/20 filter blur-sm skew-x-12"></div>
          <svg class="h-full w-20 opacity-80" viewBox="0 0 100 400" preserveAspectRatio="none">
            <path d="M50,0 Q60,100 40,200 T50,400" fill="none" stroke="#00FFF0" stroke-width="2" class="animate-pulse shadow-[0_0_15px_#00FFF0]"/>
          </svg>
        </div>

        <!-- Agent Dot 1 (Pink) -->
        <div class="absolute top-1/2 left-1/3 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-1 group">
          <div class="w-10 h-10 rounded-full border-2 border-pink-500 bg-pink-500/20 flex items-center justify-center shadow-[0_0_10px_rgba(236,72,153,0.5)] animate-pulse">
            <!-- Lucide User Icon with Gradient -->
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
          <span class="text-[9px] text-pink-400 uppercase tracking-wider group-hover:scale-110 transition-transform font-inter">Agent 1</span>
        </div>

        <!-- Agent Dot 2 (Cyan) -->
        <div class="absolute bottom-1/3 right-1/4 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-1 group">
          <div class="w-10 h-10 rounded-full border-2 border-[#00FFF0] bg-[#00FFF0]/20 flex items-center justify-center shadow-[0_0_10px_rgba(0,255,240,0.5)] animate-pulse">
            <!-- Lucide User Icon with Gradient -->
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
                <div class="h-full bg-pink-500 w-[92%] shadow-[0_0_5px_rgba(236,72,153,0.8)]"></div>
              </div>
              <span class="text-[9px] text-gray-400 w-6 text-right font-mono">92%</span>
            </div>
            <div class="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-pink-500">
                <path d="m13 2-2 2.5L9 7l3 3-2 2.5L8 15l3 3-2 2.5L7 23"/>
                <path d="M11 2 9 4.5 7 7l3 3-2 2.5L6 15l3 3-2 2.5L5 23"/>
              </svg>
              <div class="h-1.5 flex-1 bg-gray-800 rounded-full overflow-hidden">
                <div class="h-full bg-pink-400 w-[87%] shadow-[0_0_5px_rgba(244,114,182,0.8)]"></div>
              </div>
              <span class="text-[9px] text-gray-400 w-6 text-right font-mono">87%</span>
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
                <div class="h-full bg-[#00FFF0] w-[92%] shadow-[0_0_5px_rgba(0,255,240,0.8)]"></div>
              </div>
              <span class="text-[9px] text-gray-400 w-6 text-right font-mono">92%</span>
            </div>
            <div class="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[#00FFF0]">
                <path d="m13 2-2 2.5L9 7l3 3-2 2.5L8 15l3 3-2 2.5L7 23"/>
                <path d="M11 2 9 4.5 7 7l3 3-2 2.5L6 15l3 3-2 2.5L5 23"/>
              </svg>
              <div class="h-1.5 flex-1 bg-gray-800 rounded-full overflow-hidden">
                <div class="h-full bg-[#00FFF0]/70 w-[87%] shadow-[0_0_5px_rgba(0,255,240,0.6)]"></div>
              </div>
              <span class="text-[9px] text-gray-400 w-6 text-right font-mono">87%</span>
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
</style>
