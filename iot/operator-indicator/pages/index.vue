<script setup lang="ts">
import type { OperatorStatus } from '~/types/status'

// State
const status = ref<OperatorStatus | null>(null)
const isConnected = ref(false)
const viewState = ref<'idle' | 'intro_video' | 'show_start_button' | 'dashboard'>('idle')
let socket: WebSocket | null = null

// Header time
const currentTime = ref('')
const currentDate = ref('')

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  const dateStr = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  currentDate.value = dateStr
}

let timeTimer: ReturnType<typeof setInterval>

const config = useRuntimeConfig()

const connectWebSocket = () => {
  try {
    socket = new WebSocket(config.public.wsUrl)

    socket.onopen = () => {
      isConnected.value = true
    }

    socket.onmessage = (event) => {
      try {
        const newStatus = JSON.parse(event.data) as OperatorStatus
        console.log("⬇️ WS RECEIVED:", newStatus)
        status.value = newStatus
      } catch (e) {
        console.error('Failed to parse WebSocket message')
      }
    }

    socket.onclose = () => {
      isConnected.value = false
      status.value = null
      setTimeout(connectWebSocket, 3000)
    }

    socket.onerror = () => {
      socket?.close()
    }

  } catch (err) {
    // Silent fail
  }
}

const playIntroOnClick = () => {
  if (viewState.value === 'idle') {
    viewState.value = 'intro_video'
  }
}

const onIntroVideoEnded = () => {
  // Show the start button overlay
  viewState.value = 'show_start_button'
}

const startMission = () => {
  // Send WebSocket message with start_system = true
  if (socket && socket.readyState === WebSocket.OPEN) {
    const payload = { start_system: true }
    socket.send(JSON.stringify(payload))
    console.log("⬆️ WS SENT:", payload)
  } else {
    console.error("WebSocket not connected")
  }
  
  // Transition to dashboard
  viewState.value = 'dashboard'
}

onMounted(() => {
  connectWebSocket()
  updateTime()
  timeTimer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (socket) {
    socket.close()
  }
  if (timeTimer) {
    clearInterval(timeTimer)
  }
})
</script>

<template>
  <div class="h-screen w-screen overflow-hidden bg-black text-[#00FFC2] flex flex-col">
    <header 
      v-if="viewState !== 'idle'" 
      class="flex justify-center items-center py-5 px-4 relative z-50 flex-shrink-0"
    >
      <div class="font-inter font-regular text-sm flex items-center bg-black/60 border border-[#00FFF0]/30 rounded-full px-8 py-3 gap-3 shadow-[0_0_15px_rgba(0,255,240,0.15)] backdrop-blur-md">
        <img src="/logo-rift-opération.png" alt="logo" class="h-8 w-8 object-contain" />
        <span class="tracking-wide text-gray-400 uppercase">MISSION: RIFT OPERATION</span>
        <span class="h-5 w-px bg-gray-600/50"></span>
        <span class="text-[#00FFC2] tracking-wider tabular-nums">{{ currentTime }}</span>
        <span class="text-gray-500">{{ currentDate }}</span>
      </div>
    </header>

    <!-- CONTENT AREA -->
    <div class="flex-1 relative overflow-hidden">
      <!-- IDLE: Logo Animation -->
      <div 
        v-if="viewState === 'idle'" 
        @click="playIntroOnClick"
        class="absolute inset-0 z-10 flex items-center justify-center cursor-pointer"
      >
        <video 
          src="/video/Logo-Animation.mp4" 
          autoplay 
          loop 
          muted 
          playsinline
          class="w-full h-full object-cover">
        </video>
        <!-- Connection Indicator -->
        <div class="absolute bottom-4 right-4 text-xs font-mono text-white/20 uppercase">
          {{ isConnected ? 'SYSTEM ONLINE' : 'WAITING FOR SIGNAL...' }}
        </div>
      </div>
      <!-- INTRO VIDEO -->
      <div v-if="viewState === 'intro_video'" class="absolute inset-0 flex items-center justify-center p-4 z-10">
        <VideoPlayer 
          videoSrc="/video/Intro-Directeur.mp4" 
          :onVideoEnd="onIntroVideoEnded" 
        />
        <!-- Background Effects -->
        <div class="fixed inset-0 pointer-events-none -z-10 opacity-10"
          style="background-image: linear-gradient(#00FFF0 1px, transparent 1px), linear-gradient(90deg, #00FFF0 1px, transparent 1px); background-size: 50px 50px;">
        </div>
      </div>
      <!-- VIDEO WITH START BUTTON -->
      <div v-if="viewState === 'show_start_button'" class="absolute inset-0 flex items-center justify-center p-4 z-10">
        <VideoPlayer 
          videoSrc="/video/Intro-Directeur.mp4" 
        />
        <StartButton :onStart="startMission" />
        <!-- Background Effects -->
        <div class="fixed inset-0 pointer-events-none -z-10 opacity-10"
          style="background-image: linear-gradient(#00FFF0 1px, transparent 1px), linear-gradient(90deg, #00FFF0 1px, transparent 1px); background-size: 50px 50px;">
        </div>
      </div>
      <!-- DASHBOARD (Bento Grid) -->
      <div v-if="viewState === 'dashboard'" class="absolute inset-0">
        <OperatorDashboard :status="status" />
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
