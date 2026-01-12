<template>
    <div class="flex flex-col items-center w-full gap-4 text-center">
        <h2 class="font-bold text-3xl md:text-5xl text-stranger-rose uppercase tracking-wide m-0">
            Question {{ question.step }}
        </h2>

        <!-- Image at top (default) -->
        <img v-if="question.image && question.imagePosition !== 'bottom'" :src="question.image"
            :alt="`Question ${question.step} image`" class="w-24 h-24 md:w-32 md:h-32 object-contain" />

        <p class="text-lg md:text-2xl text-stranger-blue leading-snug m-0 max-w-xl whitespace-pre-line"
            v-html="question.text"></p>

        <!-- Image at bottom -->
        <img v-if="question.image && question.imagePosition === 'bottom'" :src="question.image"
            :alt="`Question ${question.step} image`" class="w-24 h-24 md:w-32 md:h-32 object-contain" />
    </div>
</template>

<script setup lang="ts">
import type { Question } from '~/config/questions'

interface Props {
    question: Question
}

defineProps<Props>()
</script>
