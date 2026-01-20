<script setup lang="ts">
import type { OperatorStatus } from '~/types/status'

// State
const status = ref<OperatorStatus | null>(null)
const isConnected = ref(false)
const viewState = ref<'idle' | 'intro_video' | 'show_start_button' | 'dashboard' | 'outro_video'>('idle')
const sockets: WebSocket[] = []
const ports = [8000, 8001, 8002]
const connectedPorts = ref<Set<number>>(new Set())

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
  // Clear existing
  sockets.forEach(s => s.close())
  sockets.length = 0
  connectedPorts.value.clear()

  const baseUrl = config.public.wsUrl.replace('ws://', '').split(':')[0] // Extract IP "192.168.10.7" from config if needed, or hardcode.
  // Actually config has full URL. Let's assume the IP is consistent with the user request.
  // User said: "8000... 8001... 8002".
  // Let's use the explicit IP from the user request to be safe: 192.168.10.7.
  const targetIp = '192.168.10.7'

  ports.forEach(port => {
    try {
      const socket = new WebSocket(`ws://${targetIp}:${port}/ws`)
      sockets.push(socket)

      socket.onopen = () => {
        console.log(`✅ WS Connected to port ${port}`)
        connectedPorts.value.add(port)
        isConnected.value = true
      }

      socket.onmessage = (event) => {
        try {
          const newStatus = JSON.parse(event.data) as OperatorStatus
          // console.log(`⬇️ WS RECEIVED (${port}):`, newStatus)
          status.value = newStatus
        } catch (e) {
          console.error(`Failed to parse WebSocket message from port ${port}`)
        }
      }

      socket.onclose = () => {
        console.log(`❌ WS Closed on port ${port}`)
        connectedPorts.value.delete(port)
        if (connectedPorts.value.size === 0) {
          isConnected.value = false
        }
        // Simple reconnect logic for individual socket could be complex. 
        // For now, if all close, we might want to retry global connect or just let it be.
        // User didn't specify robust retry logic for individual ports, so we left it simple.
      }

      socket.onerror = () => {
        console.error(`WS Error on port ${port}`)
        socket?.close()
      }

    } catch (err) {
      console.error(`Failed to create connection for port ${port}`, err)
    }
  })
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
  // Send WebSocket message with start_system = true to ALL ports
  const payload = { 
    start_system: true,
    device_id: 'OPERATOR-MONITOR' 
  }
  
  let sentCount = 0
  sockets.forEach(socket => {
    if (socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(payload))
      sentCount++
    }
  })
  
  if (sentCount > 0) {
    console.log(`⬆️ WS SENT to ${sentCount} ports:`, payload)
  } else {
    console.error("No WebSocket connected")
  }
  
  // Transition to dashboard
  viewState.value = 'dashboard'
}

const showOutro = () => {
  viewState.value = 'outro_video'
}

onMounted(() => {
  connectWebSocket()
  updateTime()
  timeTimer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  sockets.forEach(s => s.close())
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
        <OperatorDashboard :status="status" @showOutro="showOutro" />
      </div>
      
      <!-- OUTRO VIDEO -->
      <div v-if="viewState === 'outro_video'" class="absolute inset-0 flex items-center justify-center p-4 z-10">
        <VideoPlayer 
          videoSrc="/video/outro-directeur.mp4" 
        />
        <!-- Background Effects -->
        <div class="fixed inset-0 pointer-events-none -z-10 opacity-10"
          style="background-image: linear-gradient(#00FFF0 1px, transparent 1px), linear-gradient(90deg, #00FFF0 1px, transparent 1px); background-size: 50px 50px;">
        </div>
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
