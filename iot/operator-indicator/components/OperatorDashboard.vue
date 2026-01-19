<script setup lang="ts">
const props = defineProps<{
  status: any
}>()

const currentTime = ref('')
const currentDate = ref('')

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  currentDate.value = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

let timer: NodeJS.Timer
onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  clearInterval(timer)
})
</script>

<template>
  <div class="h-screen w-screen bg-black text-[#00E5FF] p-4 font-mono overflow-hidden flex flex-col gap-4">
    
    <!-- HEADER -->
    <header class="flex justify-center items-center py-2 border border-[#00E5FF]/30 rounded-full bg-black/50 backdrop-blur-sm relative mb-2">
      <div class="flex items-center gap-4">
         <div class="w-8 h-8 bg-pink-600 rounded flex items-center justify-center font-bold text-black skew-x-[-12deg]">R</div>
         <span class="tracking-widest uppercase text-sm text-gray-400">MISSION: RIFT OPERATION</span>
         <span class="h-4 w-px bg-gray-600"></span>
         <span class="text-[#00E5FF] font-bold">{{ currentTime }}</span>
         <span class="text-gray-500 text-sm">{{ currentDate }}</span>
      </div>
    </header>

    <div class="grid grid-cols-12 grid-rows-12 gap-4 flex-1 mb-4">

      <!-- BRIEFING DE MISSION (Top Left) -->
      <div class="col-span-7 row-span-6 border border-[#00E5FF]/30 rounded-xl p-6 relative group overflow-hidden">
        <div class="absolute inset-0 bg-[#00E5FF]/5 group-hover:bg-[#00E5FF]/10 transition-colors pointer-events-none"></div>
        <div class="absolute top-0 right-0 p-2 text-[#00E5FF]/20 text-4xl font-thin">⌝</div>
        <div class="absolute bottom-0 left-0 p-2 text-[#00E5FF]/20 text-4xl font-thin">⌞</div>
        
        <h2 class="flex items-center gap-2 text-lg uppercase tracking-widest mb-12">
          <span class="i-heroicons-exclamation-circle w-6 h-6"></span>
          Briefing de Mission
        </h2>
        
        <div class="text-4xl leading-tight font-bold text-yellow-400 max-w-2xl glowing-text">
          Monde 1: Identifier le prénom de l'étranger en collaborant entre les différents mondes
        </div>
      </div>

      <!-- TABLEAU DE BORD AGENT (Top Right) -->
      <div class="col-span-5 row-span-6 border border-[#00E5FF]/30 rounded-xl p-4 relative flex flex-col">
        <h2 class="text-lg uppercase tracking-widest mb-4 border-b border-[#00E5FF]/20 pb-2">Tableau de bord Agent</h2>
        
        <div class="flex-1 grid grid-cols-2 gap-4">
           <!-- MAP placeholder -->
           <div class="border border-gray-800 rounded bg-gray-900/50 relative overflow-hidden flex items-center justify-center">
             <div class="absolute inset-0 flex items-center justify-center opacity-20">
               <div class="w-px h-full bg-[#00E5FF] blur-[2px]"></div>
               <div class="h-px w-full bg-[#00E5FF] blur-[2px] absolute"></div>
             </div>
             <span class="text-xs text-gray-600">GEOLOCALISATION...</span>
           </div>

           <!-- AGENTS LIST -->
           <div class="flex flex-col gap-4 justify-center">
             <!-- Agent 1 -->
             <div class="border border-pink-500/30 bg-pink-500/5 rounded p-3">
               <div class="flex items-center gap-3 mb-2">
                 <div class="w-8 h-8 rounded-full border border-pink-500 flex items-center justify-center text-pink-500">
                    <span class="i-heroicons-user w-4 h-4"></span>
                 </div>
                 <div>
                    <div class="text-pink-500 font-bold text-sm">Agent 1</div>
                    <div class="text-[10px] text-gray-400 uppercase">Navigateur Onirique</div>
                 </div>
               </div>
               <div class="space-y-1">
                 <div class="h-1 w-full bg-gray-800 rounded overflow-hidden">
                   <div class="h-full bg-pink-500 w-[92%]"></div>
                 </div>
                 <div class="h-1 w-full bg-gray-800 rounded overflow-hidden">
                   <div class="h-full bg-pink-400 w-[87%]"></div>
                 </div>
               </div>
             </div>

             <!-- Agent 2 -->
             <div class="border border-[#00E5FF]/30 bg-[#00E5FF]/5 rounded p-3">
               <div class="flex items-center gap-3 mb-2">
                 <div class="w-8 h-8 rounded-full border border-[#00E5FF] flex items-center justify-center text-[#00E5FF]">
                    <span class="i-heroicons-user w-4 h-4"></span>
                 </div>
                 <div>
                    <div class="text-[#00E5FF] font-bold text-sm">Agent 2</div>
                    <div class="text-[10px] text-gray-400 uppercase">Chasseur de Cachemars</div>
                 </div>
               </div>
               <div class="space-y-1">
                 <div class="h-1 w-full bg-gray-800 rounded overflow-hidden">
                   <div class="h-full bg-[#00E5FF] w-[92%]"></div>
                 </div>
                 <div class="h-1 w-full bg-gray-800 rounded overflow-hidden">
                   <div class="h-full bg-[#00E5FF]/70 w-[87%]"></div>
                 </div>
               </div>
             </div>

           </div>
        </div>
      </div>

      <!-- AVANCÉE DE LA MISSION (Bottom Left) -->
      <div class="col-span-3 row-span-6 border border-[#00E5FF]/30 rounded-xl p-4 flex flex-col">
         <h2 class="text-lg uppercase tracking-widest mb-4">Avancée</h2>
         <div class="grid grid-cols-2 grid-rows-2 gap-3 flex-1">
            <div class="border border-[#00E5FF] rounded bg-[#00E5FF]/10 flex flex-col items-center justify-center text-center p-2">
               <span class="text-2xl font-bold text-[#00E5FF]">01:33</span>
               <span class="text-[10px] text-gray-400 leading-tight">Temps passé<br>dans la faille</span>
            </div>
            <div class="border border-yellow-500 rounded bg-yellow-500/10 flex flex-col items-center justify-center text-center p-2">
               <span class="text-2xl font-bold text-yellow-500">2</span>
               <span class="text-[10px] text-gray-400 leading-tight">Morceaux<br>récupérés</span>
            </div>
            <div class="border border-yellow-500 rounded bg-yellow-500/10 flex flex-col items-center justify-center text-center p-2">
               <span class="text-2xl font-bold text-yellow-500">4</span>
               <span class="text-[10px] text-gray-400 leading-tight">Morceaux<br>restants</span>
            </div>
            <div class="border border-[#00E5FF] rounded bg-[#00E5FF]/10 flex flex-col items-center justify-center text-center p-2">
               <span class="text-xl font-bold text-[#00E5FF]">2,50m</span>
               <span class="text-[10px] text-gray-400 leading-tight">Largeur<br>faille</span>
            </div>
         </div>
      </div>

      <!-- MONITEUR DE FAILLE (Bottom Center) -->
      <div class="col-span-4 row-span-6 border border-[#00E5FF]/30 rounded-xl p-4 flex flex-col">
         <div class="flex justify-between items-end mb-2">
            <h2 class="text-lg uppercase tracking-widest">Moniteur</h2>
            <span class="text-[#00E5FF]">33.33%</span>
         </div>
         <div class="w-full h-1 bg-gray-800 rounded mb-4">
            <div class="h-full bg-gradient-to-r from-pink-500 to-[#00E5FF] w-1/3"></div>
         </div>
         <div class="flex-1 border border-gray-800 bg-black relative flex items-center justify-center overflow-hidden">
            <!-- Simulated Waveform -->
             <div class="flex items-end gap-1 h-32">
                <div v-for="i in 20" :key="i" 
                     class="w-2 bg-[#00E5FF] animate-pulse" 
                     :style="{ height: Math.random() * 100 + '%' }">
                </div>
             </div>
         </div>
      </div>

       <!-- FLUX DE COMMUNICATION (Bottom Right) -->
       <div class="col-span-5 row-span-6 border border-[#00E5FF]/30 rounded-xl p-4 flex flex-col relative overflow-hidden">
         <div class="flex justify-between items-center mb-4 border-b border-[#00E5FF]/20 pb-2">
            <h2 class="text-lg uppercase tracking-widest flex items-center gap-2">
               <span class="i-heroicons-wifi w-5 h-5 animate-pulse"></span>
               Flux de Communication
            </h2>
            <div class="flex items-center gap-1 text-[10px] text-[#00E5FF]">
               <span class="w-1.5 h-1.5 rounded-full bg-[#00E5FF]"></span>
               DIRECT
            </div>
         </div>

         <div class="space-y-4 text-xs font-mono overflow-y-auto pr-1">
            <div class="opacity-80">
               <div class="flex justify-between text-gray-500 mb-0.5">
                  <span class="text-[#00E5FF]">AGENT-02</span>
                  <span>14:23:15</span>
               </div>
               <div class="text-gray-300">Fragment trouvé derrière la banquise !</div>
            </div>

            <div class="opacity-80">
               <div class="flex justify-between text-gray-500 mb-0.5">
                  <span class="text-[#00E5FF]">AGENT-02</span>
                  <span>14:23:42</span>
               </div>
               <div class="text-gray-300">Homme inconnu qui hante le cauchemars détectée</div>
            </div>

            <div class="opacity-100 border-l-2 border-pink-500 pl-2">
               <div class="flex justify-between text-gray-500 mb-0.5">
                  <span class="text-pink-500">AGENT-01</span>
                  <span>14:24:31</span>
               </div>
               <div class="text-gray-300">Question 3 résolu grâce à Cosmo</div>
            </div>
            
            <div class="opacity-100 border-l-2 border-pink-500 pl-2">
               <div class="flex justify-between text-gray-500 mb-0.5">
                  <span class="text-pink-500">AGENT-01</span>
                  <span>14:24:08</span>
               </div>
               <div class="text-gray-300">Question 1 trouvée</div>
            </div>
         </div>

      </div>

    </div>

  </div>
</template>

<style scoped>
.glowing-text {
  text-shadow: 0 0 10px rgba(250, 204, 21, 0.5);
}
</style>
