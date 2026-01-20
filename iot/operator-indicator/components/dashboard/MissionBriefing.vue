<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import type { OperatorStatus } from '~/types/status'

const props = defineProps<{
  status: OperatorStatus | null
}>()

// Mission briefing state machine
const briefingState = ref(0)
const highestStateReached = ref(0)
const title = ref('BRIEFING DE MISSION')
const message = ref('')
let stateTimer: ReturnType<typeof setTimeout> | null = null

// Briefing content configuration
const briefingContent: Record<number, { title: string; message: string; nextState?: number; delay?: number }> = {
  0: {
    title: 'BRIEFING DE MISSION',
    message: `<strong>Objectif :</strong><br> Résoudre les <u>3 mondes interdimensionnels</u>, récupérer les fragments de faille correspondants et procéder à la fermeture de la faille !<br><br><strong>Opérateur</strong>, vous disposez d'un système de communication <span class="font-semibold">talkie-walkie</span> (appareil devant vous) pour transmettre instructions et directives à vos agents sur le terrain.`,
    nextState: 1,
    delay: 30000
  },
  1: {
    title: 'ÉTAPE DE MISSION',
    message: `<strong class="text-3xl">Monde 1</strong> :<br> Identifier l'<u>identité</u> du sujet inconnu en coordonnant les informations entre les secteurs dimensionnels.`,
    nextState: 2,
    delay: 30000
  },
  2: {
    title: 'DIRECTIVE',
    message: `Consultez le <strong>dossier d'investigation</strong>. Les agents précédents y ont compilé des <u>données essentielles</u> qui faciliteront votre progression dans les différents mondes !`
  },
  3: {
    title: 'SUCCÈS MONDE 1',
    message: `<strong class="text-3xl text-green-400">✓ Identification du sujet confirmée</strong><br><br>L'identité de l'inconnu a été établie avec succès !`,
    nextState: 4,
    delay: 10000
  },
  4: {
    title: 'LOCALISATION FRAGMENTS',
    message: `<strong>Fragments de faille localisés :</strong><br><br>
<span class="text-pink-400">•</span> <strong>Secteur Rêve</strong> : derrière la grosse sucette<br>
<span class="text-[#00FFC2]">•</span> <strong>Secteur Cauchemar</strong> : derrière la banquise en formation<br><br>
Vous pouvez placer les fragments sur le socle pour initier le processus de stabilisation de la faille dimensionnelle`
  },
  5: {
    title: 'STABILISATION EN COURS',
    message: `Les agents ont initié le processus de <strong>stabilisation de la breche dimensionnel</strong>.<br><br><strong class="text-3xl">Opérateur</strong>, activez maintenant le <u>dispositif lumineux</u> pour engager la phase de fermeture de la faille !`
  },
  6: {
    title: 'DIRECTIVE',
    message: `<strong class="text-green-400">Excellent travail !</strong><br><br>Transition vers le <strong class="text-3xl">Monde 2</strong> : jouez la musique spécifique pour faire fuir l'inconnu dans le dernier secteur dimensionnel pour le confronter`
  },
  7: {
    title: 'SUCCÈS MONDE 2',
    message: `<strong class="text-3xl text-green-400">✓ Monde 2 sécurisé</strong><br><br>L'inconnu a été repoussé avec succès dans le dernier secteur dimensionnel. Préparez-vous pour la phase finale de la mission !`,
    nextState: 8,
    delay: 10000
  },
  8: {
    title: 'LOCALISATION FRAGMENTS',
    message: `<strong>Fragments de faille localisés :</strong><br><br>
<span class="text-pink-400">•</span> <strong>Secteur Rêve</strong> : derrière le banc de poisson<br>
<span class="text-[#00FFC2]">•</span> <strong>Secteur Cauchemar</strong> : derrière les algues du xylophone<br><br>`
  },
  9: {
    title: 'STABILISATION EN COURS',
    message: `Les agents ont initié le processus de <strong>stabilisation de la breche dimensionnel</strong>.<br><br><strong class="text-3xl">Opérateur</strong>, activez maintenant le <u>dispositif lumineux</u> pour engager la phase de fermeture de la faille !`
  },
  10: {
    title: 'DIRECTIVE',
    message: `<strong class="text-green-400">Excellent travail !</strong><br><br>Transition vers le <strong class="text-3xl">Monde 3</strong> : affrontez l'inconnu directement pour l'affaiblir et ainsi le capturer définitivement !`,
    nextState: 11,
    delay: 15000
  },
  11: {
    title: 'SUPPORT TACTIQUE',
    message: `Regardez les notes laissées par les agents précédents pour savoir comment combattre l'inconnu`
  },
  12: {
    title: 'ARMEMENT PRÊT',
    message: `Les armes dessinées par vos agents semblent pouvoir contrer l'attaque de l'inconnu.<br><br>Appuyer sur le <strong>bouton lumineux</strong> pour lancer le contre contre l'inconnu !`
  },
  13: {
    title: 'IMPACT CONFIRMÉ',
    message: `<strong class="text-green-400">Bravo !</strong> Le contre semble efficace !<br>Continuez comme ça pour l'affaiblir suffisamment afin de le capturer`,
    nextState: 11,
    delay: 5000
  },
  14: {
    title: 'CIBLE AFFAIBLIE',
    message: `<strong class="text-3xl text-red-500 animate-pulse">ATTENTION !</strong><br><br>L'inconnu est assez affaibli pour être capturé !<br><strong>ALLEZ-Y OPÉRATEUR : PLACEZ LA CAGE SUR LA BOÎTE POUR LE CAPTURER !</strong>`
  },
  15: {
    title: 'VICTOIRE',
    message: `<strong class="text-4xl text-green-400">FÉLICITATIONS !</strong><br><br>L'inconnu a été capturé avec succès !`,
    nextState: 16,
    delay: 10000
  },
  16: {
    title: 'LOCALISATION FINALE',
    message: `<strong>Derniers fragments de faille localisés :</strong><br><br>Les deux se trouvent sous la petite excroissance de la souche d'arbre`
  },
  17: {
    title: 'STABILISATION FINALE',
    message: `La faille est en cours de fermeture définitive.<br><br><strong class="text-3xl">Opérateur</strong>, initiez la procédure de verrouillage finale !`
  },
  18: {
    title: 'MISSION ACCOMPLIE',
    message: `<strong class="text-4xl text-purple-400">BRAVO LES AGENTS !</strong><br><br>La faille est complètement refermée ! C'est du beau boulot pour des nouveaux !<br>Agents sur le terrain, vous pouvez revenir dans le sas pour le discord du directeur et le débriefing`
  }
}

// Function to update content based on state
const updateContent = (state: number) => {
  const content = briefingContent[state]
  if (!content) return

  title.value = content.title
  message.value = content.message

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
  if (newStrangerState === 'inactive' && briefingState.value === 2 && highestStateReached.value <= 2) {
    briefingState.value = 3
  }
})

watch(() => [props.status?.battle_drawing_dream_recognised, props.status?.battle_drawing_nightmare_recognised], ([dream, nightmare]) => {
  if (dream && nightmare && briefingState.value === 11 && highestStateReached.value <= 11) {
    briefingState.value = 12
  }
})

watch(() => props.status?.battle_hit_confirmed, (hit) => {
  // If we are in "Weapons Ready" (12), go to "Hit Confirmed" (13)
  if (hit === true && briefingState.value === 12 && highestStateReached.value <= 12) {
    briefingState.value = 13
  }
})

watch(() => props.status?.battle_state, (state) => {
  // Weakened logic
  if ((state === 'Weakened' || state === 'WEAKENED') && briefingState.value < 14) {
    // Jump to Weakened regardless of loop state
    briefingState.value = 14
    highestStateReached.value = 14 // Force update
  }
  // Captured logic
  if ((state === 'Captured' || state === 'CAPTURED') && briefingState.value === 14 && highestStateReached.value <= 14) {
    briefingState.value = 15
  }
})

watch(() => props.status?.rift_part_count, (newCount) => {
  if (newCount === 2 && briefingState.value === 4 && highestStateReached.value <= 4) {
    briefingState.value = 5
  }
  if (newCount === 4 && briefingState.value === 8 && highestStateReached.value <= 8) {
    briefingState.value = 9
  }
  // World 3 Fragments (6 total) -> Case 17 (Stabilisation Final)
  // Actually user said: "when we receive rfid_part_count=6, we display the same message then [localisation]" -> "fragments located" is case 16.
  // Wait, the flow is: Victory (15) -> wait 10s -> Localisation (16).
  // THEN "when receive count=6" -> Stabilisation (17).
  if (newCount === 6 && briefingState.value === 16 && highestStateReached.value <= 16) {
    briefingState.value = 17
  }
})

watch(() => props.status?.operator_launch_close_rift_step_3, (launched) => {
  if (launched === true && briefingState.value === 17 && highestStateReached.value <= 17) {
    briefingState.value = 18
  }
})

watch(() => props.status?.depth_state, (newState) => {
  if ((newState === 'inactive' || newState === 'Inactive') && briefingState.value === 6 && highestStateReached.value <= 6) {
    briefingState.value = 7
  }
})

watch(() => props.status?.operator_launch_close_rift_step_1, (launched) => {
  if (launched === true && briefingState.value === 5 && highestStateReached.value <= 5) {
    briefingState.value = 6
  }
})

watch(() => props.status?.operator_launch_close_rift_step_2, (launched) => {
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
      class="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider mb-5 text-[#00FFC2] font-orbitron">
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
