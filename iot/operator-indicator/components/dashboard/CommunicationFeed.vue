<script setup lang="ts">
const props = defineProps<{
  messages?: Array<{
    agent: string
    time: string
    text: string
    color: 'cyan' | 'pink'
  }>
}>()

// Default mock messages if not provided
const defaultMessages = [
  { agent: 'AGENT-02', time: '14:23:15', text: 'Fragment trouvé derrière la banquise !', color: 'cyan' as const },
  { agent: 'AGENT-02', time: '14:23:42', text: 'Homme inconnu qui hante le cauchemars détectée', color: 'cyan' as const },
  { agent: 'AGENT-01', time: '14:24:31', text: 'Question 3 résolu grâce à Cosmo', color: 'pink' as const },
  { agent: 'AGENT-01', time: '14:24:08', text: 'Question 1 trouvée', color: 'pink' as const },
]

const displayMessages = computed(() => props.messages || defaultMessages)
</script>

<template>
  <div class="col-span-5 row-span-6 border border-[#00FFC2]/30 rounded-xl p-5 flex flex-col relative overflow-hidden bg-[#050809]">
    <div class="flex justify-between items-center mb-5 pb-2 border-b border-[#00FFC2]/20">
      <h2 class="text-sm font-semibold uppercase tracking-wider flex items-center gap-2 text-[#00FFC2] font-inter">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="animate-pulse">
          <path d="M5 22h14"/>
          <path d="M5 2h14"/>
          <path d="M17 22v-4.172a2 2 0 0 0-.586-1.414L12 12l-4.414 4.414A2 2 0 0 0 7 17.828V22"/>
          <path d="M7 2v4.172a2 2 0 0 0 .586 1.414L12 12l4.414-4.414A2 2 0 0 0 17 6.172V2"/>
        </svg>
        Flux de Communication
      </h2>
      <div class="flex items-center gap-2 text-[10px] tracking-widest text-[#00FFC2] uppercase px-2 py-1 bg-[#00FFC2]/10 rounded border border-[#00FFC2]/20 font-inter">
        <span class="w-1.5 h-1.5 rounded-full bg-[#00FFC2] animate-ping"></span>
        Direct
      </div>
    </div>

    <div class="space-y-3 overflow-y-auto pr-2 custom-scrollbar flex-1">
      <div 
        v-for="(msg, idx) in displayMessages" 
        :key="idx"
        :class="[
          'p-3 rounded-r hover:bg-opacity-60 transition-colors border-l-2',
          msg.color === 'cyan' ? 'bg-gray-900/50 border-[#00FFF0]' : 'bg-pink-900/10 border-pink-500'
        ]"
      >
        <div class="flex justify-between text-xs mb-1">
          <span 
            :class="[
              'font-bold tracking-wider font-orbitron',
              msg.color === 'cyan' ? 'text-[#00FFF0]' : 'text-pink-500'
            ]"
          >
            {{ msg.agent }}
          </span>
          <span class="text-gray-500 font-mono">{{ msg.time }}</span>
        </div>
        <div class="text-gray-300 text-sm font-light font-inter">{{ msg.text }}</div>
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

/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(0, 255, 240, 0.2);
  border-radius: 2px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 255, 240, 0.5);
}
</style>
