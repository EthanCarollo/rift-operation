<template>
    <div class="flex justify-center gap-[1vw] p-[0.5vw]">
        <div v-for="step in totalSteps" :key="step"
            class="relative w-[5vw] h-[5vw] flex items-center justify-center transition-transform duration-300 hover:scale-110">
            <!-- Candy image - fill for current/past steps, not-fill for future -->
            <img :src="step <= currentStep ? '/images/fill-candy.png' : '/images/not-fill-candy.png'" alt=""
                class="absolute inset-0 w-full h-full object-contain" />

            <!-- Step number - yellow for active, dark blue for inactive -->
            <span class="relative z-10 font-bold text-[1.5vw]"
                :style="{ color: step <= currentStep ? '#FFFF00' : '#150059' }">{{ step }}</span>
        </div>
    </div>
</template>

<script setup lang="ts">
interface Props {
    currentStep: number
    totalSteps?: number
}

withDefaults(defineProps<Props>(), {
    totalSteps: 4
})
</script>
