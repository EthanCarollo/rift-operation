<template>
  <div class="h-full w-full overflow-hidden flex items-center justify-center">
    <WebcamGrid 
      mode="selection"
      :initial-selected="selectedWebcams"
      :initial-rotations="webcamRotations"
      :initial-filters="webcamFilters"
      @continue="handleContinue"
    />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from '#app'
import { useRiftState } from '~/composables/useRiftState'

const router = useRouter()
const { selectedWebcams, webcamRotations, webcamFilters } = useRiftState()

const handleContinue = (selection: Record<string, string>, rotations: Record<string, number>, filters: Record<string, { grayscale: boolean, fnaf: boolean }>) => {
  selectedWebcams.value = selection
  webcamRotations.value = rotations
  webcamFilters.value = filters
  router.push('/standby')
}
</script>
