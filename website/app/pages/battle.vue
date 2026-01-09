<template>
  <div class="fixed inset-0 bg-black flex flex-col overflow-hidden font-mono select-none" @click="unlockAudio">

    <!-- 1. ROLL SELECTION SCREEN (Initial State) -->
    <div v-if="!selectedRole" class="absolute inset-0 z-50 flex flex-col items-center justify-center bg-[#0a0a0a]">
      <div class="grid place-items-center gap-12">
        <div
          class="relative w-32 h-32 border-4 border-purple-500/30 rounded-full animate-pulse flex items-center justify-center">
          <div class="w-24 h-24 border-2 border-purple-500/60 rounded-full" />
          <div class="absolute w-full h-[2px] bg-purple-500 animate-[scan_2s_ease-in-out_infinite] opacity-50" />
        </div>
        <div class="text-center space-y-3">
          <h1 class="text-4xl font-black tracking-[0.2em] text-purple-400 glitch-text">
            BATAILLE FINALE
          </h1>
          <p class="text-sm tracking-widest opacity-70 uppercase text-purple-300 mb-8">
            EN ATTENTE DES AGENTS
          </p>
          <!-- Role Buttons -->
          <div class="flex gap-8 justify-center">
            <button @click="selectedRole = 'dream'"
              class="px-8 py-3 bg-pink-600/20 border border-pink-500/50 hover:bg-pink-600/40 hover:scale-105 text-pink-300 font-bold tracking-widest rounded transition-all duration-300 uppercase shadow-[0_0_20px_rgba(219,39,119,0.2)]">
              Dream
            </button>
            <button @click="selectedRole = 'nightmare'"
              class="px-8 py-3 bg-blue-600/20 border border-blue-500/50 hover:bg-blue-600/40 hover:scale-105 text-blue-300 font-bold tracking-widest rounded transition-all duration-300 uppercase shadow-[0_0_20px_rgba(37,99,235,0.2)]">
              Nightmare
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. BATTLE VIEW (Role Selected) -->
    <template v-else>
      <!-- Background Video (Only if NOT Idle) -->
      <video v-show="currentVideo && !videoError && battleState !== 'IDLE'" ref="videoRef"
        class="absolute inset-0 w-full h-full object-cover z-0" :src="currentVideo" autoplay loop muted playsinline
        @error="handleVideoError" @loadeddata="onVideoLoaded" />

      <!-- IDLE STATE (Minimal Black Screen + Status) -->
      <div v-if="battleState === 'IDLE'" class="absolute inset-0 z-10 bg-black flex items-center justify-center">
        <!-- Minimal status provided by BattleHUD below -->
      </div>

      <!-- BATTLE UI OVERLAY -->
      <div class="absolute inset-0 z-10 pointer-events-none">
        <!-- HUD always present to show connection status even in IDLE -->
        <BattleHUD ref="hudRef" :is-connected="isConnected" :show-debug="showDebug" :state="battleState" :hp="currentHp"
          :attack="currentAttack" :video-name="currentVideo?.split('/').pop() || 'None'" :current-music="currentMusic"
          :should-loop="musicShouldLoop" @simulate="simulateRecon" @capture="simulateCapture" />

        <!-- Game Components (Only if NOT Idle) -->
        <template v-if="battleState !== 'IDLE'">
          <BattleBoss v-if="!isEndState" :is-hit="isHit" :attack="currentAttack" />
          <BattleAgent v-if="!isEndState" :dream-valid="dreamCounterValid" :nightmare-valid="nightmareCounterValid"
            :is-attacking="isAttacking" :drawing-data="currentRoleDrawing" @attack="triggerAttack" />
          <BattleState :message="stateMessage" :sub-message="stateSubMessage" :message-class="stateMessageClass" />
        </template>
      </div>
    </template>

  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import BattleHUD from '~/components/battle/BattleHUD.vue';
import BattleBoss from '~/components/battle/BattleBoss.vue';
import BattleAgent from '~/components/battle/BattleAgent.vue';
import BattleState from '~/components/battle/BattleState.vue';
import { useBattleState } from '~/composables/useBattleState';

definePageMeta({ layout: false });

// --- CONFIG ---
const showDebug = ref(true);
const selectedRole = ref(null); // 'dream' | 'nightmare' | null

// --- COMPOSABLE ---
const {
  // State
  battleState,
  currentHp,
  currentAttack,
  currentVideo,
  currentMusic,
  musicShouldLoop,
  dreamDrawingImage,
  nightmareDrawingImage,
  isAttacking,
  isHit,
  videoError,
  isConnected,

  // Counters
  dreamCounterValid,
  nightmareCounterValid,

  // Messages
  stateMessage,
  stateSubMessage,
  stateMessageClass,

  // Refs
  hudRef,
  videoRef,

  // Actions
  init,
  triggerAttack,
  simulateCapture,
  simulateRecon,
  unlockAudio,
  handleVideoError,
  onVideoLoaded
} = useBattleState(showDebug.value);

// --- COMPUTED ---
const isEndState = computed(() => {
  return battleState.value === 'WEAKENED' || battleState.value === 'CAPTURED';
});

const currentRoleDrawing = computed(() => {
  if (selectedRole.value === 'dream') return dreamDrawingImage.value;
  if (selectedRole.value === 'nightmare') return nightmareDrawingImage.value;
  return null;
});

// --- LIFECYCLE ---
onMounted(() => {
  init();
});
</script>

<style scoped>
@keyframes scan {
  0% {
    top: 0%;
    opacity: 0;
  }

  50% {
    opacity: 1;
  }

  100% {
    top: 100%;
    opacity: 0;
  }
}

.glitch-text {
  text-shadow: 2px 0 #a855f7, -2px 0 #06b6d4;
  animation: glitch 3s infinite alternate-reverse;
}

@keyframes glitch {
  0% {
    transform: skewX(0deg);
    opacity: 1;
  }

  5% {
    transform: skewX(10deg);
    opacity: 0.8;
  }

  10% {
    transform: skewX(-10deg);
    opacity: 1;
  }

  15%,
  100% {
    transform: skewX(0deg);
    opacity: 1;
  }
}
</style>
