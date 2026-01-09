<template>
  <transition name="fade">
    <div v-if="message"
      class="absolute inset-0 z-50 flex flex-col items-center justify-center bg-black/80 backdrop-blur-sm pointer-events-none">
      <h1 class="text-5xl md:text-7xl font-black text-white mb-6 text-center" :class="messageClass">
        {{ message }}
      </h1>
      <p v-if="subMessage" class="text-xl md:text-2xl text-white/70 max-w-2xl text-center leading-relaxed">
        {{ subMessage }}
      </p>
    </div>
  </transition>
</template>

<script setup>
defineProps({
  message: String,
  subMessage: String,
  messageClass: String
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
