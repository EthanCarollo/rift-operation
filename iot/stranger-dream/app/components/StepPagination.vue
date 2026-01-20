<template>
    <div class="flex justify-center gap-[1vw] p-[0.5vw]">
        <div v-for="step in totalSteps" :key="step"
            class="relative w-[5vw] h-[2.5vw] flex items-center justify-center transition-transform duration-300 hover:scale-110">
            <!-- Candy shape with double spikes -->
            <svg viewBox="0 0 100 50" class="absolute inset-0 w-full h-full drop-shadow-md">
                <!-- Left spikes -->
                <polygon points="20,15 0,5 10,15" :fill="step <= currentStep ? '#FF00CF' : '#00FFC4'" />
                <polygon points="20,35 0,45 10,35" :fill="step <= currentStep ? '#FF00CF' : '#00FFC4'" />
                <polygon points="20,15 10,15 10,35 20,35" :fill="step <= currentStep ? '#FF00CF' : '#00FFC4'" />

                <!-- Center oval -->
                <ellipse cx="50" cy="25" rx="32" ry="22" :fill="step <= currentStep ? '#FF00CF' : '#00FFC4'" />

                <!-- Right spikes -->
                <polygon points="80,15 100,5 90,15" :fill="step <= currentStep ? '#FF00CF' : '#00FFC4'" />
                <polygon points="80,35 100,45 90,35" :fill="step <= currentStep ? '#FF00CF' : '#00FFC4'" />
                <polygon points="80,15 90,15 90,35 80,35" :fill="step <= currentStep ? '#FF00CF' : '#00FFC4'" />
            </svg>

            <!-- Step number -->
            <span class="relative z-10 font-bold text-[1.5vw] text-stranger-blue">{{ step }}</span>
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
