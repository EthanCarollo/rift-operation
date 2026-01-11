<template>
    <div class="step-pagination">
        <div v-for="step in totalSteps" :key="step" class="step-item" :class="{ 'step-active': step <= currentStep }">
            <!-- Candy shape with double spikes -->
            <svg viewBox="0 0 100 50" class="step-candy">
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
            <span class="step-number">{{ step }}</span>
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

<style scoped>
.step-pagination {
    display: flex;
    justify-content: center;
    gap: 0.75rem;
    padding: 0.5rem;
}

.step-item {
    position: relative;
    width: 70px;
    height: 35px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.3s ease;
}

.step-item:hover {
    transform: scale(1.1);
}

.step-candy {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.15));
}

.step-number {
    position: relative;
    z-index: 2;
    font-family: 'Lineal', 'Fredoka One', cursive;
    font-size: 1.25rem;
    font-weight: bold;
    color: #150059;
    text-shadow: none;
}

@media (max-width: 640px) {
    .step-pagination {
        gap: 0.4rem;
    }

    .step-item {
        width: 55px;
        height: 28px;
    }

    .step-number {
        font-size: 1rem;
    }
}
</style>
