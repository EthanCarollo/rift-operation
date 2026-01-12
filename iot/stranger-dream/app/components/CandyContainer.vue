<template>
    <div class="relative flex items-center justify-center w-full max-w-4xl mx-auto">
        <!-- Candy image background -->
        <img src="/images/stranger/question-container-candy.png" alt="" class="w-full h-auto block" />

        <!-- Content overlay -->
        <div class="absolute inset-0 flex flex-col items-center justify-center px-[18%] pt-[10%] pb-[18%] text-center">
            <!-- Main content (centered) -->
            <div class="flex-1 flex flex-col items-center justify-center w-full">
                <slot></slot>
            </div>
        </div>

        <!-- Pagination (fixed at absolute bottom) -->
        <div class="absolute bottom-[12%] left-1/2 -translate-x-1/2 w-full px-[18%]">
            <slot name="pagination"></slot>
        </div>
    </div>
</template>

<script setup lang="ts">
</script>
