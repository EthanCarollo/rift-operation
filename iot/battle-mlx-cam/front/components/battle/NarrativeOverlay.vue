<template>
    <Transition name="fade">
        <div v-if="show" class="absolute top-[15%] left-0 right-0 z-20 flex justify-center pointer-events-none">
            <div class="bg-black/80 px-8 py-4 rounded-lg max-w-2xl text-center">
                <p class="text-white text-lg md:text-xl font-medium leading-relaxed animate-fade-in">
                    {{ text }}
                </p>
            </div>
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
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>
