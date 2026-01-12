<template>
    <div class="relative flex items-start justify-center w-full max-w-4xl mx-auto">
        <!-- Candy image background -->
        <img src="/images/stranger/question-container-candy.png" alt="" class="relative w-full h-auto block" />

        <!-- Content -->
        <div class="absolute inset-0 z-10 flex flex-col items-center px-8 justify-start text-center">
            <!-- Main content (centered) -->
            <div class=" flex-1 flex flex-col items-center justify-start w-full px-48 pb-8 pt-12">
                <slot></slot>
            </div>
        </div>

        <!-- Pagination (fixed at absolute bottom) -->
        <div class="absolute bottom-[8%] left-1/2 -translate-x-1/2 w-full px-[18%]">
            <slot name="pagination"></slot>
        </div>
    </div>
</template>

<script setup lang="ts">
</script>
