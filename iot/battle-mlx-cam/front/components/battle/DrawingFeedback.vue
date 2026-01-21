<template>
    <Transition name="bounce">
        <div v-if="show" class="absolute bottom-[35%] left-1/2 transform -translate-x-1/2 z-30 transition-all duration-300">
            
            <!-- Validation Badge -->
            <div v-if="!isLoading" class="px-6 py-3 rounded-full text-lg font-bold animate-bounce"
                :class="isValid ? 'bg-green-500 text-white' : 'bg-red-500/80 text-white'">
                {{ isValid ? '✓ Dessin validé !' : '✗ Essayez autre chose...' }}
            </div>
            
            <!-- Loading Bar for AI Generation -->
            <div v-else class="flex flex-col items-center gap-3">
                <div class="text-white text-lg font-medium animate-pulse">🎨 Génération en cours...</div>
                <div class="w-64 h-2 bg-neutral-700 rounded-full overflow-hidden">
                    <div class="h-full bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500 rounded-full animate-loading-bar"></div>
                </div>
            </div>
        </div>
    </Transition>
</template>

<script setup lang="ts">
defineProps<{
    show: boolean;
    isValid: boolean;
    isLoading: boolean;
}>();
</script>

<style scoped>
.bounce-enter-active {
    animation: bounce-in 0.3s ease;
}
.bounce-leave-active {
    animation: bounce-in 0.2s ease reverse;
}
@keyframes bounce-in {
    0% { transform: translateX(-50%) scale(0.8); opacity: 0; }
    50% { transform: translateX(-50%) scale(1.05); }
    100% { transform: translateX(-50%) scale(1); opacity: 1; }
}

.animate-loading-bar {
    animation: loading-bar 1.5s ease-in-out infinite;
    width: 30%;
}
@keyframes loading-bar {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(400%); }
}
</style>
