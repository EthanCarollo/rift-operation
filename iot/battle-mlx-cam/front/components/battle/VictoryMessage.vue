<template>
    <Transition name="fade">
        <div v-if="show" class="absolute inset-0 z-50 flex items-center justify-center bg-black/80">
            <p class="text-green-400 text-2xl md:text-3xl font-medium text-center px-8 max-w-3xl">
                {{ text }}
            </p>
        </div>
    </Transition>
</template>

<script setup lang="ts">
defineProps<{
    show: boolean;
    text: string;
}>();
</script>

<style scoped>
.fade-enter-active {
    transition: opacity 0.5s ease;
}
.fade-leave-active {
    transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>
