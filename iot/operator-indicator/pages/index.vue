<script setup lang="ts">
// State
const status = ref<any>(null)
const isConnected = ref(false)
const viewState = ref<'idle' | 'intro' | 'dashboard'>('idle')
let socket: WebSocket | null = null

// Video References
const introVideo = ref<HTMLVideoElement | null>(null)

const connectWebSocket = () => {
  try {
    socket = new WebSocket('ws://192.168.10.7:8000/ws')

    socket.onopen = () => {
      isConnected.value = true
    }

    socket.onmessage = (event) => {
      try {
        const newStatus = JSON.parse(event.data)
        status.value = newStatus

        // Trigger Transition to Intro when system starts
        if (viewState.value === 'idle' && newStatus.start_system === true) {
          playIntro()
        }
        // Force Dashboard if system is already running and we reload
        if (viewState.value === 'idle' && newStatus.start_system === true && newStatus.intro_played === true) {
             // Optional: If we had a "persisted" intro_played state in backend, we could skip.
             // For now, simpler logic: if start_system is true, we play intro unless we already did.
             // If you want to skip intro on reload, we'd need a flag. 
             // Let's stick to the requested flow: Idle -> Intro -> Dashboard.
        }

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

const playIntro = () => {
  viewState.value = 'intro'
  nextTick(() => {
    if (introVideo.value) {
      introVideo.value.play().catch(e => console.error("Autoplay prevent?", e))
    }
  })
}

const onIntroEnded = () => {
  viewState.value = 'dashboard'
}

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (socket) {
    socket.close()
  }
})
</script>

<template>
  <div class="h-screen w-screen overflow-hidden bg-black">
    
    <!-- IDLE STATE: Loop Video -->
    <div v-if="viewState === 'idle'" class="absolute inset-0 z-10 flex items-center justify-center">
       <video 
         src="/video/Logo-Animation.mp4" 
         autoplay 
         loop 
         muted 
         playsinline
         class="w-full h-full object-cover">
       </video>
       
       <!-- Debug / Connection Indicator -->
       <div class="absolute bottom-4 right-4 text-xs font-mono text-white/20 uppercase">
          {{ isConnected ? 'SYSTEM ONLINE' : 'WAITING FOR SIGNAL...' }}
       </div>
    </div>

    <!-- INTRO STATE: Transition Video -->
    <div v-if="viewState === 'intro'" class="absolute inset-0 z-20 bg-black flex items-center justify-center">
       <video 
         ref="introVideo"
         src="/video/Intro-Directeur.mp4" 
         class="w-full h-full object-cover"
         @ended="onIntroEnded">
       </video>
    </div>

    <!-- DASHBOARD STATE: Main Interface -->
    <div v-if="viewState === 'dashboard'" class="absolute inset-0 z-30">
       <OperatorDashboard :status="status" />
    </div>

  </div>
</template>
