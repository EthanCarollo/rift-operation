<script setup lang="ts">
import type { OperatorStatus } from '~/types/status'
import MissionBriefing from './dashboard/MissionBriefing.vue'
import AgentBoard from './dashboard/AgentBoard.vue'
import MissionProgress from './dashboard/MissionProgress.vue'
import RiftMonitor from './dashboard/RiftMonitor.vue'

const props = defineProps<{
  status: OperatorStatus | null
}>()

const emit = defineEmits<{
  showOutro: []
}>()
</script>

<template>
  <div class="h-full w-full bg-black text-[#00FFC2] font-inter overflow-hidden flex flex-col px-5 pb-5">

    <!-- DASHBOARD GRID -->
    <div class="grid grid-cols-12 grid-rows-12 gap-4 flex-1 relative z-10 overflow-hidden">
      <MissionBriefing :status="status" @showOutro="emit('showOutro')" />
      <AgentBoard :status="status" />
      <MissionProgress :status="status" />
      <RiftMonitor :status="status" />
    </div>

    <!-- BACKGROUND GRID FX -->
    <div class="fixed inset-0 pointer-events-none z-0 opacity-10"
      style="background-image: linear-gradient(#00FFF0 1px, transparent 1px), linear-gradient(90deg, #00FFF0 1px, transparent 1px); background-size: 50px 50px;">
    </div>
    <div class="fixed inset-0 pointer-events-none z-0 bg-radial-gradient from-transparent via-black to-black opacity-80"></div>

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
