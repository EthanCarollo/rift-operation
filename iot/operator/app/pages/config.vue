<template>
  <div class="h-full w-full overflow-hidden flex items-center justify-center">
    <WebcamGrid 
      mode="selection"
      :initial-selected="selectedWebcams"
      @continue="handleContinue"
    />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from '#app'
import { useRiftState } from '~/composables/useRiftState'

const router = useRouter()
const { selectedWebcams } = useRiftState()

const handleContinue = (selection: Record<string, string>) => {
  selectedWebcams.value = selection
  router.push('/standby')
}
</script>
