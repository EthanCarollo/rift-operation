<template>
  <div class="h-full w-full overflow-y-auto flex items-center justify-center">
    <ModeSelector @select="handleModeSelect" />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from '#app'
import { useRiftState } from '~/composables/useRiftState'

const router = useRouter()
const { appMode } = useRiftState()

const handleModeSelect = (mode: 'Dream' | 'Nightmare') => {
  appMode.value = mode
  router.push('/config')
}
</script>
