<script setup lang="ts">
import type { OperatorStatus } from '~/types/status'

const props = defineProps<{
  status: OperatorStatus | null
}>()

// Real-time timer
const elapsedTime = ref('00:00')
let startTime: number | null = null
let timerInterval: ReturnType<typeof setInterval> | null = null

const updateTimer = () => {
  if (!startTime) startTime = Date.now()
  
  const elapsed = Math.floor((Date.now() - startTime) / 1000)
  const minutes = Math.floor(elapsed / 60)
  const seconds = elapsed % 60
  elapsedTime.value = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

// Fragment tracking with no-rollback
const highestPartCount = ref(0)

const partsCollected = computed(() => {
  const newCount = props.status?.rift_part_count || 0
  // Only update if moving forward
  if (newCount > highestPartCount.value) {
    highestPartCount.value = newCount
  }
  return highestPartCount.value
})

const partsRemaining = computed(() => {
  return 6 - partsCollected.value
})

// Rift width calculation (starts at 2m, reduces by 33% each time)
const riftWidth = computed(() => {
  const count = partsCollected.value
  if (count === 0) return '2,00m'
  if (count === 2) return '1,34m'
  if (count === 4) return '0,67m'
  if (count >= 6) return '0,00m'
  return '2,00m'
})

// Listen for reset_system
watch(() => props.status?.reset_system, (reset) => {
  if (reset === true || reset === 'true' || reset === 'TRUE') {
    highestPartCount.value = 0
    startTime = Date.now()
  }
})

onMounted(() => {
  updateTimer()
  timerInterval = setInterval(updateTimer, 1000)
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<template>
  <div class="col-span-3 row-span-6 border border-[#00FFC2]/30 rounded-xl p-4 flex flex-col bg-[#050809] relative">
    <h2 class="text-lg font-semibold uppercase tracking-wider mb-5 text-[#00FFC2] font-orbitron">Avancée de la mission</h2>
    
    <div class="grid grid-cols-2 grid-rows-2 gap-4 flex-1">
      <!-- Box 1: Timer -->
      <div class="border border-[#00FFC2] rounded-xl bg-gradient-to-b from-[#00FFC2]/5 to-transparent flex flex-col items-center justify-center text-center p-2 shadow-[0_0_10px_rgba(0,255,240,0.1)]">
        <span class="text-5xl font-bold text-[#00FFC2] font-mono tracking-tighter drop-shadow-[0_0_5px_#00FFC2]">{{ elapsedTime }}</span>
        <span class="text-[10px] text-[#00FFC2]/70 mt-1 font-semibold leading-tight uppercase font-inter">Temps passé<br>dans la faille</span>
      </div>
      
      <!-- Box 2: Parts Collected -->
      <div class="border border-yellow-400 rounded-xl bg-gradient-to-b from-yellow-400/5 to-transparent flex flex-col items-center justify-center text-center p-2 shadow-[0_0_10px_rgba(250,204,21,0.1)]">
        <span class="text-6xl font-bold text-yellow-400 font-mono drop-shadow-[0_0_5px_#FACC15]">{{ partsCollected }}</span>
        <span class="text-[10px] text-yellow-400/70 mt-1 font-semibold leading-tight uppercase font-inter">Morceaux de<br>faille récupérés</span>
      </div>
      
      <!-- Box 3: Parts Remaining -->
      <div class="border border-yellow-400 rounded-xl bg-gradient-to-b from-yellow-400/5 to-transparent flex flex-col items-center justify-center text-center p-2 shadow-[0_0_10px_rgba(250,204,21,0.1)]">
        <span class="text-4xl font-bold text-yellow-400 font-mono drop-shadow-[0_0_5px_#FACC15]">{{ partsRemaining }}</span>
        <span class="text-[10px] text-yellow-400/70 mt-1 font-semibold leading-tight uppercase font-inter">Morceaux de<br>faille restants</span>
      </div>
      
      <!-- Box 4: Rift Width -->
      <div class="border border-[#00FFC2] rounded-xl bg-gradient-to-b from-[#00FFC2]/5 to-transparent flex flex-col items-center justify-center text-center p-2 shadow-[0_0_10px_rgba(0,255,240,0.1)]">
        <span class="text-5xl font-bold text-[#00FFC2] font-mono tracking-tighter drop-shadow-[0_0_5px_#00FFC2]">{{ riftWidth }}</span>
        <span class="text-[10px] text-[#00FFC2]/70 mt-1 font-semibold leading-tight uppercase font-inter">Largeur de<br>la faille</span>
      </div>
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
