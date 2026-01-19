<script setup lang="ts">
const props = defineProps<{
  onStart: () => void
}>()

const isVisible = ref(false)

onMounted(() => {
  // Trigger pop animation after a brief delay
  setTimeout(() => {
    isVisible.value = true
  }, 100)
})
</script>

<template>
  <div 
    class="fixed bottom-8 right-8 z-50 transition-all duration-500 transform"
    :class="isVisible ? 'scale-100 opacity-100' : 'scale-0 opacity-0'"
  >
    <button 
      @click="onStart"
      class="relative bg-gradient-to-r from-pink-600 to-[#00FFF0] text-white font-bold text-sm uppercase tracking-widest px-6 py-3 rounded-lg overflow-hidden transition-all duration-300 hover:scale-110 hover:shadow-[0_0_30px_rgba(236,72,153,0.8)] font-orbitron skew-x-[-12deg] animate-pulse-glow"
    >
      <span class="relative z-10 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="5 3 19 12 5 21 5 3"/>
        </svg>
        START THE MISSION
      </span>
    </button>
  </div>
</template>

<style scoped>
.font-orbitron {
  font-family: 'Orbitron', sans-serif;
}

@keyframes pulse-glow {
  0%, 100% { 
    box-shadow: 0 0 20px rgba(236, 72, 153, 0.5);
  }
  50% { 
    box-shadow: 0 0 30px rgba(236, 72, 153, 0.8), 0 0 40px rgba(0, 255, 240, 0.4);
  }
}

.animate-pulse-glow {
  animation: pulse-glow 2s ease-in-out infinite;
}
</style>
