<template>
  <div class="h-screen w-screen overflow-hidden flex flex-col transition-colors duration-500 font-mono" :class="{'dark-mode': appMode === 'Nightmare'}">
    
    <!-- Header / Status Bar - Visible if Mode Selected or on logic pages -->
    <header 
      v-if="route.path !== '/monitor'" 
      class="flex-none border-b border-[var(--border)] bg-[var(--bg-main)] p-2 flex justify-between items-center z-50 transition-all duration-300"
    >
      <div class="flex items-center gap-4">
        <h1 class="text-xs font-bold uppercase tracking-wider text-[var(--accent)] flex items-center gap-2">
          <span class="w-2 h-2 rounded-full" :class="statusColor"></span>
          Rift Operation // {{ currentPageName }}
        </h1>
      </div>
      <div class="flex gap-2 text-[10px] font-bold uppercase text-[var(--text-sec)]">
        <button 
          v-if="appMode"
          @click="handleReset" 
          class="hover:text-[var(--text-main)] border border-transparent hover:border-[var(--border)] px-2 transition-all"
        >
          Reset Config
        </button>
        <span v-if="appMode" class="px-2 border-l border-[var(--border)]">
          {{ appMode }} Mode
        </span>
        <span v-if="isActive" class="px-2 border-l border-[var(--border)] text-[var(--success)]" title="Screen Wake Lock Active">
           ⚡
        </span>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 overflow-hidden relative">
      <slot />
    </main>

    <!-- WebSocket Status Indicator -->
    <div 
      class="fixed bottom-4 right-4 w-3 h-3 rounded-full transition-colors duration-500 shadow-lg z-[100]"
      :class="isConnected ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]' : 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]'"
      :title="isConnected ? 'Connected' : 'Disconnected'"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from '#app'
import { useRiftState } from '~/composables/useRiftState'
import { useWakeLock } from '~/composables/useWakeLock'
import { useAppWebSocket } from '~/composables/useAppWebSocket'

const { appMode, resetState } = useRiftState()
const { isActive } = useWakeLock()
const { isConnected, connect } = useAppWebSocket()
const route = useRoute()
const router = useRouter()

onMounted(() => {
  connect()
})

const handleReset = () => {
  resetState()
  router.push('/')
}

const statusColor = computed(() => {
  if (!appMode.value) return 'bg-gray-500'
  return appMode.value === 'Dream' ? 'bg-blue-500' : 'bg-red-500'
})

const currentPageName = computed(() => {
  if (route.path === '/') return 'MODE SELECT'
  if (route.path === '/config') return 'CONFIG'
  if (route.path === '/monitor') return 'MONITOR'
  return 'UNKNOWN'
})
</script>
