<template>
  <div class="absolute bottom-12 left-0 right-0 flex items-end justify-center px-12 gap-8 pointer-events-none z-30">
    <!-- LEFT: Dream Status & Button (PINK) -->
    <div class="flex flex-col items-center gap-4 transition-all duration-500 pointer-events-auto">
      <button :disabled="!dreamValid || isAttacking" @click.stop="$emit('attack')"
        class="px-6 py-2 rounded text-xs font-bold tracking-widest transform transition-all duration-300"
        :class="dreamValid ? 'bg-pink-600 text-white hover:bg-pink-500 hover:scale-110 shadow-[0_0_20px_rgba(219,39,119,0.6)] animate-pulse' : 'bg-gray-800 text-gray-500 opacity-50 cursor-not-allowed'">
        LANCER
      </button>
      <div class="flex flex-col items-center gap-2" :class="dreamValid ? 'opacity-100' : 'opacity-40 grayscale'">
        <div
          class="bg-black/60 border border-pink-500/30 px-4 py-3 rounded-lg flex flex-col items-center min-w-[100px]">
          <span class="text-[10px] uppercase text-pink-400 tracking-widest mb-1">Dream</span>
          <div class="w-3 h-3 rounded-full"
            :class="dreamValid ? 'bg-pink-500 shadow-[0_0_10px_#ec4899]' : 'bg-gray-700'"></div>
        </div>
      </div>
    </div>

    <!-- CENTER: Agent Zone (Images) -->
    <div
      class="relative w-[400px] aspect-video bg-black/20 rounded-xl border border-white/10 flex items-center justify-center overflow-hidden backdrop-blur-sm transition-all duration-700 ease-in-out z-30 pointer-events-auto"
      :class="{
        'scale-105 border-yellow-400/50 shadow-[0_0_30px_rgba(250,204,21,0.2)]': dreamValid && nightmareValid,
        '!fixed !top-1/2 !left-1/2 !-translate-x-1/2 !-translate-y-1/2 !scale-[3] !opacity-0 !duration-500': isAttacking
      }">
      <template v-if="drawingData">
        <img :src="drawingData" class="w-full h-full object-contain" />
      </template>
      <div v-else class="text-white/20 text-sm uppercase tracking-widest animate-pulse">
        Scan en cours...
      </div>
    </div>

    <!-- RIGHT: Nightmare Status & Button (BLUE) -->
    <div class="flex flex-col items-center gap-4 transition-all duration-500 pointer-events-auto">
      <button :disabled="!nightmareValid || isAttacking" @click.stop="$emit('attack')"
        class="px-6 py-2 rounded text-xs font-bold tracking-widest transform transition-all duration-300"
        :class="nightmareValid ? 'bg-blue-600 text-white hover:bg-blue-500 hover:scale-110 shadow-[0_0_20px_rgba(37,99,235,0.6)] animate-pulse' : 'bg-gray-800 text-gray-500 opacity-50 cursor-not-allowed'">
        LANCER
      </button>
      <div class="flex flex-col items-center gap-2" :class="nightmareValid ? 'opacity-100' : 'opacity-40 grayscale'">
        <div
          class="bg-black/60 border border-blue-500/30 px-4 py-3 rounded-lg flex flex-col items-center min-w-[100px]">
          <span class="text-[10px] uppercase text-blue-400 tracking-widest mb-1">Nightmare</span>
          <div class="w-3 h-3 rounded-full"
            :class="nightmareValid ? 'bg-blue-500 shadow-[0_0_10px_#3b82f6]' : 'bg-gray-700'"></div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
defineProps({
  dreamValid: Boolean,
  nightmareValid: Boolean,
  isAttacking: Boolean,
  drawingData: String
});
defineEmits(['attack']);
</script>
