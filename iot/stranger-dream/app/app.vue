<template>
  <div class="min-h-screen relative overflow-hidden bg-cover bg-center bg-no-repeat cursor-none"
    :style="strangerState === 'inactive' ? { backgroundColor: 'black' } : { backgroundImage: 'url(/images/stranger/bg-candy-land.png)' }">
    <!-- Main content area -->
    <main class="relative z-10 flex flex-col items-center justify-center min-h-screen p-8">
      <template v-if="strangerState !== 'inactive'">
        <!-- Candy container with content -->
        <CandyContainer>
          <!-- Puzzle View (step 1 / active) -->
          <PuzzleView v-if="currentQuestion?.type === 'puzzle'" :question="currentQuestion" />

          <!-- Text View (step 2, 3, 4) -->
          <TextView v-else-if="currentQuestion" :question="currentQuestion" />

          <!-- Step pagination inside candy -->
          <template #pagination>
            <StepPagination :current-step="currentQuestion?.step ?? 0" :total-steps="4" />
          </template>
        </CandyContainer>
      </template>
    </main>

    <!-- Dev Panel (only in dev mode) -->
    <DevPanel v-if="isDev" :is-connected="isConnected" :current-state="strangerState" :states="availableStates"
      v-model:url-value="urlInput" @set-state="setDevState" @reconnect="handleReconnect" />
  </div>
</template>

<script setup lang="ts">
import { useStrangerSocket } from '~/composables/useStrangerSocket'
import { questions, type Question } from '~/config/questions'
import CandyContainer from '~/components/CandyContainer.vue'
import PuzzleView from '~/components/PuzzleView.vue'
import TextView from '~/components/TextView.vue'
import StepPagination from '~/components/StepPagination.vue'
import DevPanel from '~/components/DevPanel.vue'

const config = useRuntimeConfig()
const isDev = config.public.isDev

const { isConnected, strangerState, wsUrl, reconnectWithUrl } = useStrangerSocket()

// Available states for dev navigation
const availableStates = ['inactive', 'active', 'step_2', 'step_3', 'step_4', 'recognized']

// Local state for URL input
const urlInput = ref(wsUrl.value)

// Handle reconnection with new URL
const handleReconnect = () => {
  reconnectWithUrl(urlInput.value)
}

// Set state directly (dev only)
const setDevState = (state: string) => {
  strangerState.value = state
}

// Computed
const currentQuestion = computed<Question | null>(() => {
  if (!strangerState.value || strangerState.value === 'inactive') return null
  return questions[strangerState.value] || null
})
</script>

<style>
/* Font face declarations - using public folder to avoid Nuxt asset loop issues */
@font-face {
  font-family: 'Lineal';
  src: url('/fonts/Lineal-Regular.ttf') format('truetype');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'Lineal';
  src: url('/fonts/Lineal-Medium.ttf') format('truetype');
  font-weight: 500;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'Lineal';
  src: url('/fonts/Lineal-Bold.ttf') format('truetype');
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}

:root {
  color-scheme: dark;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: 'Lineal', 'Montserrat', sans-serif;
  background-color: #00FFC4;
  overflow-x: hidden;
  cursor: none;
}

/* Scrollbar Styles */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #150059;
}

::-webkit-scrollbar-thumb {
  background: #FF00CF;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #cc00a6;
}
</style>
