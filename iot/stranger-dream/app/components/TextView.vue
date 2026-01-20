<template>
    <div class="flex flex-col items-center w-full gap-[2vw] text-center">
        <div class="flex flex-col items-center w-full gap-[1vw] text-center">
            <h2 class="font-bold text-[1.8vw] text-stranger-rose uppercase tracking-wide m-0">
                {{ question.title || `Question ${question.step}` }}
            </h2>
            <p class="text-[2vw] text-stranger-blue leading-snug m-0 max-w-[60vw] whitespace-pre-line"
                v-html="question.text"></p>
        </div>

        <!-- Images side-by-side (if images array exists) -->
        <div v-if="question.images && question.images.length" class="flex justify-center items-center space-x-[-6vw]">
            <img v-for="(img, idx) in question.images" :key="idx" :src="img"
                :alt="`Question ${question.step} image ${idx + 1}`" class="w-[18vw] h-[18vw] object-contain" />
        </div>

        <!-- Image at bottom (fallback/legacy) -->
        <img v-if="question.image && question.imagePosition === 'bottom'" :src="question.image"
            :alt="`Question ${question.step} image`" class="w-[18vw] h-[18vw] object-contain" />
    </div>
</template>

<script setup lang="ts">
import type { Question } from '~/config/questions'

interface Props {
    question: Question
}

defineProps<Props>()
</script>
