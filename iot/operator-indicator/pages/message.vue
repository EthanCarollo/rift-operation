<script setup lang="ts">
// State
const status = ref<any>(null)
const isConnected = ref(false)
const error = ref<string | null>(null)
let socket: WebSocket | null = null

// --- CONFIGURATION ---
const STEPS_CONFIG = [
  { key: 'operator_launch_close_rift_step_3', label: 'FERMETURE DE LA FAILLE - TERMINÉ', percent: 100 },
  { key: 'operator_launch_close_rift_step_2', label: 'FERMETURE DE LA FAILLE - ÉTAPE 2', percent: 66 },
  { key: 'operator_launch_close_rift_step_1', label: 'FERMETURE DE LA FAILLE - ÉTAPE 1', percent: 33 },
]
// ---------------------

const connectWebSocket = () => {
  try {
    socket = new WebSocket('ws://192.168.10.7:8000/ws')

    socket.onopen = () => {
      console.log('WebSocket Connected')
      isConnected.value = true
      error.value = null
    }

    socket.onmessage = (event) => {
      try {
        status.value = JSON.parse(event.data)
      } catch (e) {
        console.error('Failed to parse WebSocket message', e)
      }
    }

    socket.onclose = () => {
      console.log('WebSocket Disconnected')
      isConnected.value = false
      status.value = null
      // Try to reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000)
    }

    socket.onerror = (err) => {
      console.error('WebSocket Error', err)
      error.value = 'Connection Error'
      socket?.close()
    }

  } catch (err) {
    console.error('WebSocket Init Error', err)
    error.value = 'Failed to Initialize WebSocket'
  }
}

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (socket) {
    socket.close()
  }
})

const displayState = computed(() => {
  if (!status.value) return { mode: 'loading', text: 'Connexion...' }

  // 1. Critical Overrides
  if (status.value.reset_system) return { mode: 'alert', text: 'RÉINITIALISATION DU SYSTÈME' }
  if (status.value.end_system) return { mode: 'alert', text: 'FIN DE LA SESSION' }
  
  // 2. Lost States
  if (status.value.lost_state) {
    if (status.value.lost_cage_is_on_monster) return { mode: 'alert', text: 'CAGE SUR MONSTRE DÉTECTÉE' }
    if (status.value.lost_light_is_triggered) return { mode: 'alert', text: 'LUMIÈRE DÉCLENCHÉE' }
    if (status.value.lost_drawing_light_recognized) return { mode: 'alert', text: 'DESSIN RECONNU' }
    return { mode: 'alert', text: 'ÉTAT PERDU ACTIF' }
  }

  // 3. System Running -> Show Progress Bar
  if (status.value.start_system) {
    let currentStep = { label: 'INITIALISATION...', percent: 0 }

    for (const step of STEPS_CONFIG) {
      if (status.value[step.key]) {
        currentStep = step
        break
      }
    }

    return { 
      mode: 'progress', 
      percent: currentStep.percent, 
      label: currentStep.label 
    }
  }

  // 4. Default / Waiting
  return { mode: 'text', text: 'EN ATTENTE...' }
})
</script>

<template>
  <div class="min-h-screen bg-white text-black font-sans relative flex flex-col items-center justify-center p-8 transition-all duration-500">
    
    <!-- HEADER / DEBUG INDICATOR (Copied style from Monitor) -->
    <div class="absolute top-6 right-6 flex items-center gap-2 text-xs uppercase tracking-wider bg-neutral-100 px-3 py-1.5 rounded-full border border-neutral-200">
       <div class="w-2 h-2 rounded-full animate-pulse" :class="isConnected ? 'bg-green-500' : 'bg-red-500'"></div>
       {{ isConnected ? 'Online' : 'Offline' }}
    </div>

    <!-- ALERT / TEXT MODE -->
    <div v-if="displayState.mode === 'alert' || displayState.mode === 'text' || displayState.mode === 'loading'" class="animate-fade-in">
      <h1 class="text-5xl md:text-7xl font-black text-center tracking-tighter uppercase leading-tight">
        {{ displayState.text }}
      </h1>
      <p v-if="!isConnected" class="text-center text-red-500 mt-4 font-mono text-sm">Waiting for connection to 192.168.10.7:8000...</p>
    </div>

    <!-- PROGRESS MODE -->
    <div v-else-if="displayState.mode === 'progress'" class="w-full max-w-5xl space-y-6 animate-slide-up">
      <!-- Label -->
      <div class="flex justify-between items-end px-1">
        <h2 class="text-2xl md:text-3xl font-bold uppercase tracking-widest">{{ displayState.label }}</h2>
        <span class="text-4xl font-mono font-black">{{ displayState.percent }}%</span>
      </div>
      
      <!-- The Bar Container -->
      <div class="h-16 w-full bg-gray-200 rounded-lg overflow-hidden relative shadow-inner border-2 border-gray-100">
        <!-- Background Pattern -->
        <div class="absolute inset-0 opacity-10" 
             style="background-image: repeating-linear-gradient(45deg, #000 0, #000 10px, transparent 10px, transparent 20px);">
        </div>

        <!-- The Fill Bar -->
        <div 
          class="h-full bg-black relative transition-all duration-1000 ease-out flex items-center justify-end overflow-hidden"
          :style="{ width: `${displayState.percent}%` }"
        >
          <!-- Shiny Effect -->
          <div class="absolute inset-0 bg-gradient-to-b from-white/20 to-transparent"></div>
          
          <!-- Animated Glow Line -->
          <div class="absolute top-0 bottom-0 right-0 w-1 bg-white/50 shadow-[0_0_20px_rgba(255,255,255,0.5)]"></div>
        </div>
      </div>

      <!-- Steps Indicators -->
      <div class="flex justify-between text-xs font-mono text-gray-400 uppercase tracking-widest pt-2">
        <span>Initialisation</span>
        <span>Synchronisation</span>
        <span>Finalisation</span>
      </div>
    </div>

  </div>
</template>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.animate-slide-up {
  animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
</style>
