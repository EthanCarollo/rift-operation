<script setup lang="ts">
const props = defineProps<{
  videoSrc: string
  onVideoEnd?: () => void
}>()

let fallbackTimer: ReturnType<typeof setTimeout> | null = null

onMounted(() => {
  if (props.onVideoEnd) {
    // Fallback: trigger after 30s if video doesn't end
    fallbackTimer = setTimeout(() => {
      props.onVideoEnd?.()
    }, 30000)
  }
})

const handleVideoEnded = () => {
  if (fallbackTimer) clearTimeout(fallbackTimer)
  props.onVideoEnd?.()
}

onUnmounted(() => {
  if (fallbackTimer) clearTimeout(fallbackTimer)
})
</script>

<template>
  <div class="w-full h-full border border-[#00FFF0]/30 rounded-2xl overflow-hidden shadow-[0_0_30px_rgba(0,255,240,0.3)] bg-black">
    <video 
      :src="videoSrc" 
      :loop="false"
      controls
      autoplay
      class="w-full h-full object-cover"
      @ended="handleVideoEnded">
    </video>
  </div>
</template>
