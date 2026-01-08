<template>
  <div class="absolute inset-0 z-20 pointer-events-none">
    <!-- TOP LEFT: Connection Status -->
    <div class="absolute top-6 left-6 flex items-center gap-3 bg-black/40 backdrop-blur px-3 py-1.5 rounded-full border border-white/10 pointer-events-auto">
      <div 
        class="w-2 h-2 rounded-full transition-colors duration-500"
        :class="isConnected ? 'bg-[#33ff00] shadow-[0_0_8px_#33ff00]' : 'bg-red-500 animate-pulse'"
      ></div>
      <span class="text-[10px] font-bold tracking-wider uppercase text-white/80">
        {{ isConnected ? 'ONLINE' : 'OFFLINE' }}
      </span>
    </div>
    <!-- TOP RIGHT: Debug Panel -->
    <div v-if="showDebug" class="absolute top-6 right-6 bg-black/60 p-3 rounded border border-white/10 text-[10px] text-white/50 font-mono leading-tight z-50 pointer-events-auto">
      <div>STATE: <span class="text-white">{{ state }}</span></div>
      <div>HP: <span class="text-white">{{ hp }}/5</span></div>
      <div>ROUND: {{ round }}</div>
      <div>ATTACK: {{ attack || 'NONE' }}</div>
      <div class="mt-1 text-purple-400">VIDEO: {{ videoName }}</div>
      <!-- DEV CONTROLS -->
      <div class="mt-2 pt-2 border-t border-white/10 flex flex-col gap-1">
        <button @click="$emit('simulate')" class="px-2 py-1 bg-blue-500/20 text-blue-300 hover:bg-blue-500/40 rounded text-center">
          Simulate Recon
        </button>
        <button @click="$emit('capture')" class="px-2 py-1 bg-purple-500/20 text-purple-300 hover:bg-purple-500/40 rounded text-center">
          Simulate Capture
        </button>
      </div>
    </div>

    <!-- TOP CENTER: Health Bar -->
    <div class="absolute top-[20%] left-0 right-0 flex justify-center">
      <div class="w-[60vw] max-w-2xl">
         <div class="flex justify-between text-xs uppercase tracking-widest text-white/60 mb-2 px-1">
           <span>Santé de l'Étranger</span>
           <span>{{ hp * 20 }}%</span>
         </div>
         <div class="flex gap-1 h-3">
          <div 
            v-for="i in 5" 
            :key="i"
            class="flex-1 rounded-sm transition-all duration-500"
            :class="i <= hp ? 'bg-gradient-to-r from-red-500 to-red-600 shadow-[0_0_12px_rgba(220,38,38,0.6)]' : 'bg-white/10'"
          ></div>
         </div>
      </div>
    </div>

  </div>
</template>

<script setup>
defineProps({
  isConnected: Boolean,
  showDebug: Boolean,
  state: String,
  hp: Number,
  round: Number,
  attack: String,
  videoName: String
});
defineEmits(['simulate', 'capture']);
</script>
