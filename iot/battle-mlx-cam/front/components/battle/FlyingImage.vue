<template>
    <div v-if="imageSrc" ref="containerRef"
        class="absolute z-40 fly-to-enemy pointer-events-none"
        :style="style">
        <img :src="imageSrc" class="w-40 h-40 object-contain drop-shadow-2xl" />
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
    imageSrc: string | null;
}>();

// Fixed starting position
const style = computed(() => ({
    left: '50%',
    bottom: '10%',
    transform: 'translateX(-50%)'
}));
</script>

<style scoped>
.fly-to-enemy {
    animation: fly-up 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
}

@keyframes fly-up {
    0% {
        bottom: 10%;
        transform: translateX(-50%) scale(1);
        opacity: 1;
    }
    70% {
        opacity: 1;
    }
    100% {
        bottom: 60%;
        transform: translateX(-50%) scale(1.5);
        opacity: 0;
    }
}
</style>
