<script setup lang="ts">
import { ref, watch, onUnmounted, onMounted } from 'vue'
import type { OperatorStatus } from '~/types/status'

const props = defineProps<{
  status: OperatorStatus | null
}>()

const emit = defineEmits<{
  showOutro: []
}>()

// Mission briefing state machine
const briefingState = ref(0)
const highestStateReached = ref(0)
const title = ref('BRIEFING DE MISSION')
const message = ref('')
let stateTimer: ReturnType<typeof setTimeout> | null = null
const audio = new Audio('/sounds/notification.mp3')

// Briefing content configuration
const briefingContent: Record<number, { title: string; message: string; nextState?: number; delay?: number }> = {
  0: {
    title: 'BRIEFING DE MISSION',
    message: `La mission va bientôt commencer...`,
    nextState: 1,
    delay: 10000
  },
  1: {
    title: 'MISSION 1',
    message: `Regardez la consigne sur les fiches devant vous et communiquez avec les autres agents`
  },
  2: {
    title: 'SUCCÈS MISSION 1',
    message: `La mission 1 est terminée !<br>Récupérez les morceaux de faille :<br><span class="text-pink-400">Rêve</span> : derrière le socle de la grosse sucette<br><span class="text-[#00FFC2]">Cauchemar</span> : derrière la banquise`
  },
  3: {
    title: 'FERMETURE FAILLE',
    message: `Les agents ont placé les morceaux de frontière.<br>Appuyez sur le bouton pour refermer la faille !`
  },
  4: {
    title: 'MISSION 2',
    message: `Regardez la consigne sur les fiches devant vous et communiquez avec les autres agents`
  },
  5: {
    title: 'SUCCÈS MISSION 2',
    message: `La mission 2 est terminée !<br>Récupérez les morceaux de faille :<br><span class="text-pink-400">Rêve</span> : derrière le banc de poisson<br><span class="text-[#00FFC2]">Cauchemar</span> : derrière les algues`
  },
  6: {
    title: 'FERMETURE FAILLE',
    message: `Les agents ont placé les morceaux de frontière.<br>Appuyez sur le bouton pour refermer la faille !`
  },
  7: {
    title: 'MISSION 3',
    message: `Regardez la consigne sur les fiches devant vous et communiquez avec les autres agents`
  },
  8: {
    title: 'SUCCÈS MISSION 3',
    message: `La mission 3 est terminée !<br>Récupérez les morceaux de faille :<br><span class="text-white">Rêve et Cauchemar</span> : sous la racine de la souche d'arbre`
  },
  9: {
    title: 'FERMETURE FAILLE',
    message: `Les agents ont placé les morceaux de frontière.<br>Appuyez sur le bouton pour refermer la faille !`
  },
  10: {
    title: 'MISSION ACCOMPLIE',
    message: `<strong class="text-6xl text-purple-400">MISSION ACCOMPLIE</strong><br><br>La faille est complètement refermée !`
  }
}

// Function to update content based on state
const updateContent = (state: number) => {
  const content = briefingContent[state]
  if (!content) return

  title.value = content.title
  message.value = content.message

  // Play sound
  audio.currentTime = 0
  audio.play().catch(e => console.log('Audio play failed (interaction needed?):', e))

  if (content.nextState !== undefined && content.delay !== undefined) {
    if (stateTimer) clearTimeout(stateTimer)
    stateTimer = setTimeout(() => {
      briefingState.value = content.nextState!
    }, content.delay)
  }
}

watch(briefingState, (newState) => {
  // Only update if moving forward or staying same
  if (newState >= highestStateReached.value) {
    highestStateReached.value = newState
    updateContent(newState)
  }
}, { immediate: true })

watch(() => props.status?.stranger_state, (newStrangerState) => {
  // Stranger Inactive -> Success Mission 1 (State 2)
  if (newStrangerState === 'inactive' && briefingState.value === 1 && highestStateReached.value <= 1) {
    briefingState.value = 2
  }
})

watch(() => props.status?.depth_state, (newState) => {
  // Depth Inactive -> Success Mission 2 (State 5)
  if ((newState === 'inactive' || newState === 'Inactive') && briefingState.value === 4 && highestStateReached.value <= 4) {
    briefingState.value = 5
  }
})

// Battle Hit / Captured logic -> Success Mission 3 (State 8)
watch(() => props.status?.battle_state, (state) => {
  if (state === 'inactive' && briefingState.value === 7 && highestStateReached.value <= 7) {
    briefingState.value = 8
  }
})

watch(() => props.status?.rift_part_count, (newCount) => {
  // 2 Parts -> Close Rift 1 (State 3)
  if (newCount === 2 && briefingState.value === 2 && highestStateReached.value <= 2) {
    briefingState.value = 3
  }
  // 4 Parts -> Close Rift 2 (State 6)
  if (newCount === 4 && briefingState.value === 5 && highestStateReached.value <= 5) {
    briefingState.value = 6
  }
  // 6 Parts -> Close Rift 3 (State 9)
  if (newCount === 6 && briefingState.value === 8 && highestStateReached.value <= 8) {
    briefingState.value = 9
  }
})

watch(() => props.status?.operator_launch_close_rift_step_1, (launched) => {
  // Button 1 Pressed -> Mission 2 (State 4)
  if (launched === true && briefingState.value === 3 && highestStateReached.value <= 3) {
    briefingState.value = 4
  }
})

watch(() => props.status?.operator_launch_close_rift_step_2, (launched) => {
  // Button 2 Pressed -> Mission 3 (State 7)
  if (launched === true && briefingState.value === 6 && highestStateReached.value <= 6) {
    briefingState.value = 7
  }
})

watch(() => props.status?.operator_launch_close_rift_step_3, (launched) => {
  // Button 3 Pressed -> Mission Accomplie (State 10)
  if (launched === true && briefingState.value === 9 && highestStateReached.value <= 9) {
    briefingState.value = 10
  }
})

watch(() => props.status?.reset_system, (reset) => {
  if (reset === true) {
    if (stateTimer) clearTimeout(stateTimer)
    briefingState.value = 0
    highestStateReached.value = 0
  }
})

// Force State Logic (Debug)
watch(() => props.status?.force_briefing_state, (forceState) => {
  if (forceState !== undefined && forceState !== null) {
    briefingState.value = forceState
    highestStateReached.value = forceState // Allow jumping back/forth
    if (stateTimer) clearTimeout(stateTimer) // Stop any auto-advance
  }
})

onUnmounted(() => {
  if (stateTimer) clearTimeout(stateTimer)
})
</script>

<template>
  <div
    class="col-span-6 row-span-6 border border-[#00FFC2]/30 rounded-xl p-5 relative group overflow-hidden bg-gradient-to-br from-[#0c1214] to-[#050809]">
    <div class="absolute top-0 right-0 p-2 border-t border-r border-[#00FFC2]/40 w-6 h-6 rounded-tr-xl"></div>
    <div class="absolute bottom-0 left-0 p-2 border-b border-l border-[#00FFC2]/40 w-6 h-6 rounded-bl-xl"></div>

    <h2
      class="flex items-center gap-2 text-3xl font-semibold uppercase tracking-wider mb-5 text-[#00FFC2] font-orbitron">
      <span class="text-4xl">⚠</span>
      {{ title }}
    </h2>

    <div class="flex flex-col justify-center h-[calc(100%-3rem)]">
      <div v-html="message"
        class="text-5xl md:text-6xl font-medium text-yellow-400 leading-relaxed tracking-normal glowing-text-yellow font-inter">
      </div>
      
      <!-- End Briefing Button (appears at state 10) -->
      <div 
        v-if="briefingState === 10"
        class="mt-8 flex justify-center"
      >
        <button 
          @click="emit('showOutro')"
          class="relative bg-pink-600 text-white font-bold text-2xl uppercase tracking-widest px-8 py-4 rounded-lg overflow-hidden transition-all duration-300 hover:bg-pink-700 hover:scale-105 hover:shadow-[0_0_30px_rgba(236,72,153,0.8)] font-orbitron skew-x-[-12deg] animate-pulse-glow"
        >
          <span class="relative z-10 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            BRIEFING DE FIN
          </span>
        </button>
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

.glowing-text-yellow {
  text-shadow:
    0 0 10px rgba(250, 204, 21, 0.6),
    0 0 20px rgba(250, 204, 21, 0.4),
    0 0 30px rgba(250, 204, 21, 0.2);
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
