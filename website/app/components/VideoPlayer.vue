<script setup lang="ts">
defineProps<{
    src: string
}>()
</script>

<template>
    <div class="my-8 rounded-xl overflow-hidden shadow-lg border border-border bg-black">
        <video :src="src" controls class="w-full aspect-video"></video>
    </div>
</template>
