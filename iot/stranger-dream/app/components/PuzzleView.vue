<template>
    <div class="flex flex-col items-center w-full gap-4">
        <h2 class="font-bold text-3xl md:text-3xl text-stranger-rose uppercase tracking-wide m-0 text-center">
            {{ question.title || `Question ${question.step}` }}
        </h2>
        <p class="text-lg md:text-xl text-stranger-blue leading-snug m-0 text-center max-w-lg">
            {{ question.subtitle }}
        </p>

        <div class="flex flex-col items-center">
            <div v-for="(item, idx) in question.puzzleItems" :key="idx"
                class="flex flex-row items-center gap-6 transition-transform duration-300 hover:scale-105 hover:rotate-2">
                <img :src="item.image" :alt="`Puzzle item ${idx + 1}`"
                    class="w-12 h-12 md:w-16 md:h-16 object-contain" />
                <div class="text-2xl text-stranger-rose">{{ item.symbol }}</div>
                <div
                    class="bg-white border-4 border-stranger-rose rounded-xl px-3 py-2 md:px-4 md:py-2 text-lg md:text-xl font-bold text-stranger-blue shadow-lg">
                    {{ item.letter }}
                </div>
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
