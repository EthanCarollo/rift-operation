<template>
    <div class="flex flex-col items-center w-full gap-4 text-center">
        <h2 v-if="question.title" class="font-bold text-2xl md:text-4xl text-stranger-rose uppercase tracking-wide m-0">
            {{ question.title }}
        </h2>
        <p class="text-lg md:text-2xl text-stranger-blue leading-snug m-0 max-w-xl whitespace-pre-line">
            {{ question.text }}
        </p>
    </div>
</template>

<script setup lang="ts">
import type { Question } from '~/config/questions'

interface Props {
    question: Question
}

defineProps<Props>()
</script>
