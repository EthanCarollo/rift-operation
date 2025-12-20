<template>
  <div class="h-full w-full flex items-center justify-center bg-[var(--bg-main)]">
    <div class="text-center animate-pulse">
      <h1 class="text-4xl font-bold tracking-[0.2em] text-[var(--accent)] mb-4">STANDBY...</h1>
      <p class="text-[var(--text-sec)] text-sm tracking-wider">WAITING FOR OPERATOR SIGNAL</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useRouter } from '#app'
import { useAppWebSocket } from '~/composables/useAppWebSocket'

const router = useRouter()
const { lastMessage } = useAppWebSocket()

watch(lastMessage, (newData) => {
  if (newData && newData.operator_start_system === true) {
    router.push('/monitor')
  }
}, { deep: true, immediate: true })
</script>
