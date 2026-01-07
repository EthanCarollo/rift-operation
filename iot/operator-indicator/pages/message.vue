<script setup lang="ts">
// State
const status = ref<any>(null)
const isConnected = ref(false)
let socket: WebSocket | null = null

// --- CONFIGURATION ---
const STEPS_CONFIG = [
  { key: 'operator_launch_close_rift_step_3', label: 'FERMETURE DE LA FAILLE - TERMINÉ', percent: 100 },
  { key: 'operator_launch_close_rift_step_2', label: 'FERMETURE DE LA FAILLE - ÉTAPE 2', percent: 66 },
  { key: 'operator_launch_close_rift_step_1', label: 'FERMETURE DE LA FAILLE - ÉTAPE 1', percent: 33 },
]

// SEQUENTIAL FLOW CONFIGURATION (Order: Strange -> Depth -> Lost)
// We check this in REVERSE order in the logic to properly handle overrides.
const EXPERIENCE_FLOW = [
  {
    field: 'lost_state',
    title: 'PROTOCOLE LOST',
    activeText: 'Confinez la créature dans la cellule pour sécuriser le fragment instable.',
    inactiveText: 'TOUS LES FRAGMENTS SONT SÉCURISÉS. POINT D\'EXTRACTION ACTIVÉ.'
  },
  {
    field: 'depth_state',
    title: 'PROTOCOLE PROFONDEUR',
    activeText: 'Reproduisez la séquence acoustique pour déverrouiller l\'accès au fragment.',
    inactiveText: 'FRAGMENT RÉCUPÉRÉ. PROCHAIN OBJECTIF : ZONE LOST.'
  },
  {
    field: 'stranger_state',
    title: 'PROTOCOLE STRANGER',
    activeText: 'Analysez les signaux pour identifier l\'entité et révéler le fragment.',
    inactiveText: 'FRAGMENT RÉCUPÉRÉ. PROCHAIN OBJECTIF : ZONE PROFONDEUR.'
  }
]
// ---------------------

const connectWebSocket = () => {
  try {
    socket = new WebSocket('ws://192.168.10.7:8000/ws')

    socket.onopen = () => {
      isConnected.value = true
    }

    socket.onmessage = (event) => {
      try {
        status.value = JSON.parse(event.data)
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
    // Silent fail, retry logic in onclose
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

// Progress Logic (Persistent)
const progress = computed(() => {
  if (!status.value || !status.value.start_system) return null

  let currentStep = { label: 'INITIALISATION DU SYSTÈME', percent: 0 }

  for (const step of STEPS_CONFIG) {
    if (status.value[step.key]) {
      currentStep = step
      break
    }
  }
  return currentStep
})

// Main Content Logic
const content = computed(() => {
  if (!status.value) return { type: 'loading', text: 'Connexion...' }

  // 1. Critical Overrides (Alerts that MUST interrupt the user immediately)
  if (status.value.reset_system) return { type: 'alert', text: 'RÉINITIALISATION DU SYSTÈME' }
  if (status.value.end_system) return { type: 'alert', text: 'FIN DE LA SESSION' }
  
  // Specific LOST sub-states that are critical alerts
  if (status.value.lost_state) {
     if (status.value.lost_cage_is_on_monster) return { type: 'alert', text: 'CAGE SUR MONSTRE DÉTECTÉE' }
     if (status.value.lost_light_is_triggered) return { type: 'alert', text: 'LUMIÈRE DÉCLENCHÉE' }
     // 'lost_drawing_light_recognized' might be kept as alert or just part of success flow? 
     // Keeping it as alert for feedback visibility:
     if (status.value.lost_drawing_light_recognized) return { type: 'alert', text: 'DESSIN RECONNU' }
  }

  // 2. Experience Flow (Instructions & Transitions)
  // We check flow in the order defined in EXPERIENCE_FLOW array ? 
  // No, we want priority: If Lost is active, we show Lost. If Lost is Inactive, we show Lost Inactive.
  // We should check the "latest" stage first.
  
  if (status.value.start_system) {
    // Check in order defined above (Lost -> Depth -> Strange)
    // Note: EXPERIENCE_FLOW is defined Lost first (index 0) to Strange (index 2).
    
    for (const exp of EXPERIENCE_FLOW) {
      const val = status.value[exp.field]
      
      // If active (truthy and not 'inactive')
      if (val && val !== 'inactive') {
        return {
          type: 'instruction',
          title: exp.title,
          text: exp.activeText,
          detail: typeof val === 'string' ? val.toUpperCase() : ''
        }
      }
      
      // If explicitly inactive
      if (val === 'inactive') {
        return {
          type: 'instruction',
          title: 'OBJECTIF SUIVANT', // Or keep the Experience Title if prefered
          text: exp.inactiveText,
          detail: 'TERMINÉ'
        }
      }
    }

    // Default Fallback (System started, but no experience has explicitly started or ended)
    return {
      type: 'instruction',
      title: 'INITIALISATION',
      text: 'SYSTÈME OPÉRATIONNEL. RENDEZ-VOUS AU SECTEUR STRANGER.',
      detail: 'EN ATTENTE'
    }
  }

  return { type: 'text', text: 'EN ATTENTE...' }
})
</script>

<template>
  <div class="min-h-screen bg-white text-black font-sans relative flex flex-col transition-all duration-500 overflow-hidden">
    
    <!-- DEBUG INDICATOR -->
    <div class="absolute top-6 right-6 z-50 flex items-center gap-2 text-xs uppercase tracking-wider bg-neutral-100 px-3 py-1.5 rounded-full border border-neutral-200">
       <div class="w-2 h-2 rounded-full animate-pulse" :class="isConnected ? 'bg-green-500' : 'bg-red-500'"></div>
       {{ isConnected ? 'Online' : 'Offline' }}
    </div>

    <!-- FULLSCREEN ALERTS (Critical) -->
    <div v-if="content.type === 'alert' || content.type === 'loading' || content.type === 'text'" 
         class="absolute inset-0 flex items-center justify-center p-8 animate-fade-in z-40 bg-white">
      <h1 class="text-5xl md:text-7xl font-black text-center tracking-tighter uppercase leading-tight">
        {{ content.text }}
      </h1>
    </div>

    <!-- MAIN LAYOUT (When System Started) -->
    <div v-else class="flex flex-col h-screen pt-24 pb-12 px-8 max-w-5xl mx-auto w-full">
      
      <!-- TOP: PERSISTENT PROGRESS BAR -->
      <div v-if="progress" class="w-full mb-12 animate-slide-down">
        <div class="flex justify-between items-end px-1 mb-2">
          <h2 class="text-xl font-bold uppercase tracking-widest">{{ progress.label }}</h2>
          <span class="text-3xl font-mono font-black">{{ progress.percent }}%</span>
        </div>
        
        <div class="h-12 w-full bg-gray-200 rounded-lg overflow-hidden relative shadow-inner border-2 border-gray-100">
          <div class="absolute inset-0 opacity-10" 
               style="background-image: repeating-linear-gradient(45deg, #000 0, #000 10px, transparent 10px, transparent 20px);">
          </div>
          <div 
            class="h-full bg-black relative transition-all duration-1000 ease-out"
            :style="{ width: `${progress.percent}%` }"
          >
            <div class="absolute inset-0 bg-gradient-to-b from-white/20 to-transparent"></div>
            <div class="absolute top-0 bottom-0 right-0 w-1 bg-white/50 shadow-[0_0_20px_rgba(255,255,255,0.5)]"></div>
          </div>
        </div>
      </div>

      <!-- BOTTOM: CONTEXTUAL INSTRUCTIONS -->
      <div v-if="content.type === 'instruction'" class="flex-1 flex flex-col justify-center animate-slide-up">
        <div class="bg-neutral-100 border-l-8 border-black p-8 rounded-r-xl shadow-sm">
          <div class="flex items-center gap-4 mb-4">
            <h3 class="text-3xl font-black uppercase tracking-tight">{{ content.title }}</h3>
            <span v-if="content.detail" class="bg-black text-white px-3 py-1 text-sm font-mono rounded">{{ content.detail }}</span>
          </div>
          <p class="text-2xl font-medium leading-relaxed text-neutral-800">
            {{ content.text }}
          </p>
        </div>
      </div>

    </div>

  </div>
</template>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in { animation: fadeIn 0.4s ease-out; }
.animate-slide-down { animation: slideDown 0.6s ease-out; }
.animate-slide-up { animation: slideUp 0.6s ease-out; }
</style>
