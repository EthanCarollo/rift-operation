<template>
    <div class="relative flex items-center justify-center w-full max-w-4xl mx-auto">
        <!-- Candy image background -->
        <img src="/images/stranger/question-container-candy.png" alt="" class="w-full h-auto block" />

        <!-- Content overlay -->
        <div class="absolute inset-0 flex flex-col items-center justify-between px-[18%] py-[12%] text-center">
            <!-- Main content (centered) -->
            <div class="flex-1 flex flex-col items-center justify-center w-full">
                <slot></slot>
            </div>

            <!-- Pagination (fixed at bottom) -->
            <div class="w-full">
                <slot name="pagination"></slot>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
</script>
