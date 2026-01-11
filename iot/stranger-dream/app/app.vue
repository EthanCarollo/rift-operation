<template>
  <div
    class="min-h-screen bg-cover bg-center bg-no-repeat flex items-center justify-center font-stranger overflow-hidden transition-all duration-1000 relative"
    :style="{ backgroundImage: 'url(/images/stranger/bg-dreamy-hires.png)' }">
    <!-- Soft overlay for dreamy feel & improved contrast -->
    <div class="absolute inset-0 bg-white/20 backdrop-blur-[2px]"></div>

    <!-- Animated Sparkles/Snow Particles -->
    <div class="absolute inset-0 z-1 pointer-events-none">
      <div class="snow snow-1"></div>
      <div class="snow snow-2"></div>
      <div class="snow snow-3"></div>
    </div>

    <div
      class="container relative z-10 flex flex-col items-center justify-center min-h-screen p-8 transition-all duration-500">

      <!-- Logo/Title (Always visible or maybe hidden when active? Request says "shows nothing" if inactive, implies showing title if inactive is base screen) -->
      <!-- Request says: "stranger_state : 'inactive' -> tu affiches rien du tout et reviens à l'écran de base" -->
      <!-- Let's assume "nothing" means no question, just the base screen (Title) -->

      <div v-if="strangerState === 'inactive'" class="transition-opacity duration-500">
        <h1
          class="text-6xl md:text-8xl text-[#4A90E2] font-black uppercase tracking-[0.2em] drop-shadow-[0_4px_8px_rgba(255,255,255,0.8)] opacity-90">

        </h1>
      </div>

      <!-- Question Overlay -->
      <div v-else class="text-center animate-pulse-slow w-full max-w-2xl px-8 relative z-10 flex flex-col items-center">

        <!-- PUZZLE TYPE -->
        <div v-if="currentQuestion && currentQuestion.type === 'puzzle'"
          class="flex flex-col items-center w-full bg-white/60 backdrop-blur-2xl p-10 rounded-[40px] border-4 border-[#FFD700]/60 shadow-[0_20px_50px_rgba(74,144,226,0.4)]">
          <h2
            class="text-[#FF1493] font-black uppercase text-3xl tracking-[0.15em] mb-4 drop-shadow-[0_2px_4px_rgba(255,255,255,1)]">
            {{ currentQuestion.title }}</h2>
          <p
            class="text-[#1E90FF] font-black text-2xl leading-tight mb-10 whitespace-pre-line text-center drop-shadow-sm">
            {{ currentQuestion.subtitle }}</p>

          <div class="flex flex-col gap-8 w-full max-w-sm">
            <div v-for="(item, idx) in currentQuestion.puzzleItems" :key="idx" class="flex items-center gap-8 group">
              <div
                class="w-24 h-24 flex items-center justify-center bg-white/80 rounded-full group-hover:scale-110 group-hover:bg-white transition-all duration-500 shadow-md border-2 border-[#B0E0E6]/50">
                <img :src="item.image" class="h-16 object-contain" />
              </div>
              <div class="text-[#FFD700] text-5xl font-black animate-bounce-x drop-shadow-[0_3px_6px_rgba(0,0,0,0.2)]">
                {{ item.symbol }}</div>
              <div
                class="bg-white w-20 h-20 rounded-2xl flex items-center justify-center text-5xl font-black text-[#1E90FF] shadow-2xl border-b-[10px] border-[#87CEEB] group-hover:scale-110 group-hover:-rotate-3 transition-all">
                {{ item.letter }}
              </div>
            </div>
          </div>
        </div>

        <!-- SIMPLE TEXT TYPE -->
        <div v-else-if="currentQuestion"
          class="bg-white/60 backdrop-blur-2xl p-12 rounded-[40px] border-4 border-[#FFD700]/60 shadow-[0_20px_50px_rgba(74,144,226,0.4)] max-w-3xl transform hover:scale-105 transition-transform duration-500">
          <h2
            class="text-[#1E90FF] font-black uppercase text-4xl md:text-5xl tracking-wide text-center leading-relaxed drop-shadow-[0_2px_4px_rgba(255,255,255,0.8)]">
            {{ currentQuestion.text }}
          </h2>
        </div>

        <!-- PROGRESS INDICATOR -->
        <div v-if="currentQuestion" class="flex gap-12 mt-16">
          <div v-for="i in 4" :key="i" class="relative group">
            <!-- Active Step -->
            <div v-if="currentQuestion.step === i" class="relative">
              <div
                class="w-16 h-16 bg-[#FFD700] rounded-full flex items-center justify-center shadow-[0_0_20px_rgba(255,215,0,0.8)] border-4 border-white animate-bounce-slow">
                <span class="text-2xl font-black text-white italic">{{ i }}</span>
              </div>
            </div>
            <!-- Inactive Step -->
            <div v-else class="relative opacity-30 group-hover:opacity-60 transition-all duration-300">
              <div class="w-12 h-12 bg-white/40 rounded-full flex items-center justify-center border-2 border-white/50">
                <span class="text-lg font-black text-[#4A90E2] italic">{{ i }}</span>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Dev-Only Status Indicator -->
      <div
        v-if="isDev"
        data-testid="dev-status-indicator"
        class="absolute top-8 right-8 bg-white/80 px-4 py-2 rounded-full flex items-center gap-2 shadow-sm backdrop-blur-sm">
        <div class="w-3 h-3 rounded-full shadow-sm transition-all duration-300"
          data-testid="connection-dot"
          :class="isConnected ? 'bg-green-400' : 'bg-red-400'"></div>
        <!-- Debug State -->
        <span class="text-xs font-bold text-gray-500 font-sans tracking-wide uppercase" data-testid="connection-status">
          {{ isConnected ? (strangerState !== 'inactive' ? strangerState : 'ONLINE') : 'CONNECTING...' }}
        </span>
      </div>

      <!-- Dev Panel for WebSocket Configuration -->
      <div
        v-if="isDev"
        data-testid="dev-panel"
        class="absolute bottom-8 right-8 bg-white/90 p-4 rounded-xl shadow-lg backdrop-blur-sm font-sans text-sm max-w-xs">
        <div class="font-bold text-gray-700 mb-2 uppercase text-xs tracking-wide">Dev Panel</div>
        <div class="flex flex-col gap-2">
          <input
            v-model="urlInput"
            type="text"
            data-testid="ws-url-input"
            placeholder="WebSocket URL"
            class="w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <button
            @click="handleReconnect"
            data-testid="reconnect-button"
            class="w-full px-3 py-2 text-xs font-bold text-white bg-blue-500 rounded-lg hover:bg-blue-600 transition-colors">
            Reconnect
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useStrangerSocket } from '~/composables/useStrangerSocket'
import { questions, type Question } from '~/config/questions'

const config = useRuntimeConfig()
const isDev = config.public.isDev

const { isConnected, strangerState, wsUrl, reconnectWithUrl } = useStrangerSocket()

// Local state for URL input
const urlInput = ref(wsUrl.value)

// Handle reconnection with new URL
const handleReconnect = () => {
  reconnectWithUrl(urlInput.value)
}

// Computed
const currentQuestion = computed<Question | null>(() => {
  if (!strangerState.value || strangerState.value === 'inactive') return null
  return questions[strangerState.value] || null
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');

.font-stranger {
  font-family: 'Montserrat', sans-serif;
}

/* Snow Animation */
.snow {
  position: absolute;
  top: -20px;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: radial-gradient(circle at center, #fff 1px, transparent 1px);
  background-size: 50px 50px;
  opacity: 0.5;
  filter: blur(1px);
}

.snow-1 {
  animation: snow-fall 10s linear infinite;
}

.snow-2 {
  animation: snow-fall 15s linear infinite;
  background-size: 80px 80px;
  opacity: 0.3;
  filter: blur(2px);
}

.snow-3 {
  animation: snow-fall 20s linear infinite;
  background-size: 150px 150px;
  opacity: 0.2;
  filter: blur(3px);
}

@keyframes snow-fall {
  0% {
    transform: translateY(-10vh) rotate(0deg);
    opacity: 0;
  }

  20% {
    opacity: 0.8;
  }

  100% {
    transform: translateY(100vh) rotate(360deg);
    opacity: 0;
  }
}

@keyframes pulse-slow {

  0%,
  100% {
    opacity: 0.95;
    transform: scale(1);
  }

  50% {
    opacity: 1;
    transform: scale(1.01);
  }
}

.animate-pulse-slow {
  animation: pulse-slow 5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes bounce-x {

  0%,
  100% {
    transform: translateX(0);
  }

  50% {
    transform: translateX(5px);
  }
}

.animate-bounce-x {
  animation: bounce-x 1.5s ease-in-out infinite;
}

@keyframes bounce-slow {

  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-10px);
  }
}

.animate-bounce-slow {
  animation: bounce-slow 2s ease-in-out infinite;
}

.container {
  max-width: 100%;
}
</style>
