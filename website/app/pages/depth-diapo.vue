<template>
  <div 
    class="fixed inset-0 overflow-hidden select-none cursor-pointer"
    @click="nextSlide"
    @keydown.right="nextSlide"
    @keydown.space="nextSlide"
    @keydown.left="prevSlide"
    @keydown.up="prevSlide"
    @keydown.down="nextSlide"
    tabindex="0"
    ref="containerRef"
  >
    <!-- Current Slide -->
    <transition name="slide-fade" mode="out-in">
      <img 
        :key="currentSlide"
        :src="slides[currentSlide]"
        class="w-full h-full object-cover"
        alt="Slide"
      />
    </transition>

    <!-- Slide Indicator (optional, subtle) -->
    <div class="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex gap-2 z-10">
      <div 
        v-for="(_, index) in slides" 
        :key="index"
        class="w-3 h-3 rounded-full transition-all duration-300"
        :class="index === currentSlide 
          ? 'bg-[#ff1493] scale-125' 
          : 'bg-white/30 hover:bg-white/50'"
        @click.stop="goToSlide(index)"
      ></div>
    </div>

    <!-- Navigation Hints (fades out) -->
    <div 
      v-if="showHints"
      class="absolute inset-0 flex items-center justify-between px-8 pointer-events-none"
    >
      <div class="text-white/50 text-6xl font-black opacity-0 animate-pulse-once">&lt;</div>
      <div class="text-white/50 text-6xl font-black opacity-0 animate-pulse-once">&gt;</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

// No layout for fullscreen experience
definePageMeta({ layout: false });

// Slides configuration - 8 slides total (5 images + 3 placeholders for now)
const slides = [
  '/depth-diapo/slide_1.jpg',
  '/depth-diapo/slide_2.jpg',
  '/depth-diapo/slide_3.jpg',
  '/depth-diapo/slide_4.jpg',
  '/depth-diapo/slide_5.jpg',
  // Add more slides here when available
  // '/depth-diapo/slide_6.jpg',
  // '/depth-diapo/slide_7.jpg',
  // '/depth-diapo/slide_8.jpg',
];

const currentSlide = ref(0);
const containerRef = ref(null);
const showHints = ref(true);

function nextSlide() {
  if (currentSlide.value < slides.length - 1) {
    currentSlide.value++;
  } else {
    // Optional: loop back to start
    currentSlide.value = 0;
  }
  hideHints();
}

function prevSlide() {
  if (currentSlide.value > 0) {
    currentSlide.value--;
  } else {
    // Optional: loop to end
    currentSlide.value = slides.length - 1;
  }
  hideHints();
}

function goToSlide(index) {
  currentSlide.value = index;
  hideHints();
}

function hideHints() {
  showHints.value = false;
}

function handleKeydown(e) {
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'ArrowDown') {
    e.preventDefault();
    nextSlide();
  } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
    e.preventDefault();
    prevSlide();
  }
}

onMounted(() => {
  // Focus container for keyboard events
  if (containerRef.value) {
    containerRef.value.focus();
  }
  // Global keyboard listener
  window.addEventListener('keydown', handleKeydown);
  
  // Hide hints after 3 seconds
  setTimeout(() => {
    showHints.value = false;
  }, 3000);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
/* Slide transition */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* Pulse once animation for hints */
@keyframes pulse-once {
  0%, 100% { opacity: 0; }
  50% { opacity: 0.3; }
}

.animate-pulse-once {
  animation: pulse-once 2s ease-in-out;
}
</style>
