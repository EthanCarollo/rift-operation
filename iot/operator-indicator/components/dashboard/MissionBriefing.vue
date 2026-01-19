<script setup lang="ts">
import type { OperatorStatus } from '~/types/status'

const props = defineProps<{
  status: OperatorStatus | null
}>()

// Mission briefing state machine
const briefingState = ref(0)
const highestStateReached = ref(0) // Track highest state to prevent rollback
const title = ref('BRIEFING DE MISSION')
const message = ref('')
let stateTimer: ReturnType<typeof setTimeout> | null = null

// Function to update content based on state
const updateContent = (state: number) => {
  switch (state) {
    case 0:
      title.value = 'BRIEFING DE MISSION'
      message.value = `<strong>Objectif :</strong><br> Résoudre les <u>3 mondes interdimensionnels</u>, récupérer les fragments de faille correspondants et procéder à la fermeture de la faille !<br><br><strong>Opérateur</strong>, vous disposez d'un système de communication <span class="font-semibold">talkie-walkie</span> (appareil devant vous) pour transmettre instructions et directives à vos agents sur le terrain.`
      if (stateTimer) clearTimeout(stateTimer)
      stateTimer = setTimeout(() => {
        briefingState.value = 1
      }, 30000)
      break

    case 1:
      title.value = 'ÉTAPE DE MISSION'
      message.value = `<strong class="text-3xl">Monde 1</strong> :<br> Identifier l'<u>identité</u> du sujet inconnu en coordonnant les informations entre les secteurs dimensionnels.`
      if (stateTimer) clearTimeout(stateTimer)
      stateTimer = setTimeout(() => {
        briefingState.value = 2
      }, 30000)
      break

    case 2:
      title.value = 'DIRECTIVE'
      message.value = `Consultez le <strong>dossier d'investigation</strong>. Les agents précédents y ont compilé des <u>données essentielles</u> qui faciliteront votre progression dans les différents mondes !`
      break

    case 3:
      title.value = 'SUCCÈS MONDE 1'
      message.value = `<strong class="text-3xl text-green-400">✓ Identification du sujet confirmée</strong><br><br>L'identité de l'inconnu a été établie avec succès !`
      if (stateTimer) clearTimeout(stateTimer)
      stateTimer = setTimeout(() => {
        briefingState.value = 4
      }, 10000)
      break

    case 4:
      title.value = 'LOCALISATION FRAGMENTS'
      message.value = `<strong>Fragments de faille localisés :</strong><br><br>
<span class="text-pink-400">•</span> <strong>Secteur Rêve</strong> : derrière la grosse sucette<br>
<span class="text-[#00FFC2]">•</span> <strong>Secteur Cauchemar</strong> : derrière la banquise en formation<br><br>`
      break

    case 5:
      title.value = 'STABILISATION EN COURS'
      message.value = `Les agents ont initié le processus de <strong>stabilisation de la breche dimensionnel</strong>.<br><br><strong class="text-3xl">Opérateur</strong>, activez maintenant le <u>dispositif lumineux</u> pour engager la phase de fermeture de la faille !`
      break

    case 6:
      title.value = 'ÉTAPE DE MISSION'
      message.value = `<strong class="text-green-400">Excellent travail !</strong><br><br>Transition vers le <strong class="text-3xl">Monde 2</strong> : investigation en cours...`
      break
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
  if (newStrangerState === 'inactive' && briefingState.value === 2 && highestStateReached.value <= 2) {
    briefingState.value = 3
  }
})

watch(() => props.status?.rift_part_count, (newCount) => {
  if (newCount === 2 && briefingState.value === 4 && highestStateReached.value <= 4) {
    briefingState.value = 5
  }
})

watch(() => props.status?.operator_launch_close_rift_step_1, (launched) => {
  if (launched === true && briefingState.value === 5 && highestStateReached.value <= 5) {
    briefingState.value = 6
  }
})

watch(() => props.status?.reset_system, (reset) => {
  if (reset === true || reset === 'true' || reset === 'TRUE') {
    if (stateTimer) clearTimeout(stateTimer)
    briefingState.value = 0
    highestStateReached.value = 0
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

    <h2 class="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider mb-5 text-[#00FFC2] font-orbitron">
      <span class="text-base">⚠</span>
      {{ title }}
    </h2>

    <div class="flex flex-col justify-center h-[calc(100%-3rem)]">
      <div v-html="message"
        class="text-xl md:text-2xl font-medium text-yellow-400 leading-relaxed tracking-normal glowing-text-yellow font-inter">
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
</style>
