<template>
    <div class="puzzle-view">
        <h2 class="puzzle-title">{{ question.title }}</h2>
        <p class="puzzle-subtitle">{{ question.subtitle }}</p>

        <div class="puzzle-grid">
            <div v-for="(item, idx) in question.puzzleItems" :key="idx" class="puzzle-item">
                <img :src="item.image" :alt="`Puzzle item ${idx + 1}`" class="puzzle-image" />
                <div class="puzzle-symbol">{{ item.symbol }}</div>
                <div class="puzzle-letter">{{ item.letter }}</div>
            </div>
        </div>
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
.puzzle-view {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    gap: 1rem;
}

.puzzle-title {
    font-family: 'Lineal', sans-serif;
    font-weight: bold;
    font-size: 2.5rem;
    color: #FF00CF;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0;
    text-align: center;
}

.puzzle-subtitle {
    font-family: 'Lineal', sans-serif;
    font-size: 1.5rem;
    color: #150059;
    line-height: 1.3;
    margin: 0;
    text-align: center;
    max-width: 500px;
}

.puzzle-grid {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin-top: 1rem;
    flex-wrap: wrap;
}

.puzzle-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    transition: transform 0.3s ease;
}

.puzzle-item:hover {
    transform: scale(1.05) rotate(2deg);
}

.puzzle-image {
    width: 64px;
    height: 64px;
    object-fit: contain;
}

.puzzle-symbol {
    font-size: 2rem;
    color: #FF00CF;
}

.puzzle-letter {
    background-color: white;
    border: 4px solid #FF00CF;
    border-radius: 12px;
    padding: 0.5rem 1rem;
    font-family: 'Lineal', sans-serif;
    font-size: 1.5rem;
    font-weight: bold;
    color: #150059;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

@media (max-width: 640px) {
    .puzzle-title {
        font-size: 1.75rem;
    }

    .puzzle-subtitle {
        font-size: 1.125rem;
    }

    .puzzle-grid {
        gap: 1rem;
    }

    .puzzle-image {
        width: 48px;
        height: 48px;
    }

    .puzzle-letter {
        font-size: 1.25rem;
        padding: 0.375rem 0.75rem;
    }
}
</style>
