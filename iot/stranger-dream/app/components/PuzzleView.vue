<template>
    <div class="flex flex-col items-center w-full gap-[1.5vw]">
        <h2 class="font-bold text-[2.5vw] text-stranger-rose uppercase tracking-wide m-0 text-center">
            {{ question.title || `Question ${question.step}` }}
        </h2>
        <p class="text-[1.5vw] text-stranger-blue leading-snug m-0 text-center max-w-[80vw]">
            {{ question.subtitle }}
        </p>

        <div class="flex flex-col items-center gap-[1vw]">
            <div v-for="(item, idx) in question.puzzleItems" :key="idx"
                class="flex flex-row items-center gap-[2vw] transition-transform duration-300 hover:scale-105 hover:rotate-2">
                <img :src="item.image" :alt="`Puzzle item ${idx + 1}`" class="w-[6vw] h-[6vw] object-contain" />
                <div class="text-[2.5vw] text-stranger-rose">{{ item.symbol }}</div>
                <div
                    class="bg-white border-[0.3vw] border-stranger-rose rounded-[1vw] px-[1.5vw] py-[0.75vw] text-[2vw] font-bold text-stranger-blue shadow-lg">
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
