<template>
  <div class="fixed inset-0 bg-black flex flex-col overflow-hidden font-mono select-none" @click="unlockAudio">
    <!-- 1. VIDEO LAYER (Background) -->
    <video v-show="currentVideo && !videoError && battleState !== 'IDLE'" ref="videoRef"
      class="absolute inset-0 w-full h-full object-cover z-0" :src="currentVideo" autoplay loop muted playsinline
      @error="handleVideoError" @loadeddata="onVideoLoaded" />

    <!-- 2. IDLE STATE (Waiting Screen) -->
    <div v-if="battleState === 'IDLE'"
      class="absolute inset-0 z-10 flex flex-col items-center justify-center bg-[#0a0a0a]">
      <div class="grid place-items-center gap-6">
        <div
          class="relative w-32 h-32 border-4 border-purple-500/30 rounded-full animate-pulse flex items-center justify-center">
          <div class="w-24 h-24 border-2 border-purple-500/60 rounded-full" />
          <div class="absolute w-full h-[2px] bg-purple-500 animate-[scan_2s_ease-in-out_infinite] opacity-50" />
        </div>
        <div class="text-center space-y-2">
          <h1 class="text-4xl font-black tracking-[0.2em] text-purple-400 glitch-text">
            BATAILLE FINALE
          </h1>
          <p class="text-sm tracking-widest opacity-70 uppercase text-purple-300">
            EN ATTENTE DES AGENTS
          </p>
        </div>
      </div>
    </div>

    <!-- 3. BATTLE UI OVERLAY (Active Game) -->
    <div v-if="battleState !== 'IDLE'" class="absolute inset-0 z-10 pointer-events-none">
      <BattleHUD ref="hudRef" :is-connected="isConnected" :show-debug="showDebug" :state="battleState" :hp="currentHp"
        :attack="currentAttack" :video-name="currentVideo?.split('/').pop() || 'None'" :current-music="currentMusic"
        :should-loop="musicShouldLoop" @simulate="simulateRecon" @capture="simulateCapture" />
      <BattleBoss v-if="!isEndState" :is-hit="isHit" :attack="currentAttack" />
      <BattleAgent v-if="!isEndState" :dream-valid="dreamCounterValid" :nightmare-valid="nightmareCounterValid"
        :is-attacking="isAttacking" :drawing-data="drawingData" @attack="triggerAttack" />
      <BattleState :message="stateMessage" :sub-message="stateSubMessage" :message-class="stateMessageClass" />
    </div>
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

// --- COMPOSABLE ---
const {
  // State
  battleState,
  currentHp,
  currentAttack,
  currentVideo,
  currentMusic,
  musicShouldLoop,
  drawingData,
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
