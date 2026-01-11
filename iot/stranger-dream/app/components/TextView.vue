<template>
    <div class="text-view">
        <h2 v-if="question.title" class="text-title">{{ question.title }}</h2>
        <p class="text-content">{{ question.text }}</p>
    </div>
</template>

<script setup lang="ts">
import type { Question } from '~/config/questions'

interface Props {
    question: Question
}

defineProps<Props>()
</script>

<style scoped>
.text-view {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    gap: 1.5rem;
    text-align: center;
}

.text-title {
    font-family: 'Lineal', sans-serif;
    font-weight: bold;
    font-size: 2.5rem;
    color: #FF00CF;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0;
}

.text-content {
    font-family: 'Lineal', sans-serif;
    font-size: 2rem;
    color: #150059;
    line-height: 1.2;
    margin: 0;
    max-width: 550px;
    white-space: pre-line;
}

@media (max-width: 768px) {
    .text-title {
        font-size: 1.75rem;
    }

    .text-content {
        font-size: 1.5rem;
    }
}

@media (max-width: 480px) {
    .text-title {
        font-size: 1.5rem;
    }

    .text-content {
        font-size: 1.25rem;
    }
}
</style>
