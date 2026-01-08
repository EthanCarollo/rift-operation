<template>
  <div class="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
    <div class="text-center" :class="{'animate-shake': isHit}">
      <h2 class="text-6xl md:text-8xl font-black text-white tracking-widest drop-shadow-2xl mix-blend-overlay opacity-90 transition-colors duration-100" 
          :class="{'text-red-500 opacity-100': isHit}">
        L'ÉTRANGER
      </h2>
      <div v-if="attack" class="mt-4 inline-block px-4 py-1 bg-yellow-500/20 border border-yellow-500/50 rounded text-yellow-500 text-sm font-bold uppercase tracking-widest animate-pulse">
        ⚠️ ATTAQUE : {{ attack }}
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isHit: Boolean,
  attack: String
});
</script>

<style scoped>
@keyframes shake {
  0% { transform: translate(1px, 1px) rotate(0deg); }
  10% { transform: translate(-1px, -2px) rotate(-1deg); }
  20% { transform: translate(-3px, 0px) rotate(1deg); }
  30% { transform: translate(3px, 2px) rotate(0deg); }
  40% { transform: translate(1px, -1px) rotate(1deg); }
  50% { transform: translate(-1px, 2px) rotate(-1deg); }
  60% { transform: translate(-3px, 1px) rotate(0deg); }
  70% { transform: translate(3px, 1px) rotate(-1deg); }
  80% { transform: translate(-1px, -1px) rotate(1deg); }
  90% { transform: translate(1px, 2px) rotate(0deg); }
  100% { transform: translate(1px, -2px) rotate(-1deg); }
}

.animate-shake {
  animation: shake 0.5s;
}
</style>
