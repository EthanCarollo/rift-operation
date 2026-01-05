<template>
  <div class="h-full w-full overflow-hidden flex items-center justify-center">
    <WebcamGrid 
      mode="selection"
      :initial-selected="selectedWebcams"
      :initial-rotations="webcamRotations"
      @continue="handleContinue"
    />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from '#app'
import { useRiftState } from '~/composables/useRiftState'

const router = useRouter()
const { selectedWebcams, webcamRotations } = useRiftState()

const handleContinue = (selection: Record<string, string>, rotations: Record<string, number>) => {
  selectedWebcams.value = selection
  webcamRotations.value = rotations
  router.push('/standby')
}
</script>
