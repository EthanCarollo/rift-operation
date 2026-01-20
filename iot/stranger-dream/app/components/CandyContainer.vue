<template>
    <div class="relative flex items-start justify-center w-[80vw] mx-auto">
        <!-- Candy image background -->
        <img src="/images/stranger/candy.png" alt="" class="relative w-full h-auto block" />

        <!-- Content -->
        <div class="absolute inset-0 z-10 flex flex-col items-center px-[4vw] h-full justify-start text-center">
            <!-- Main content (centered) -->
            <div class="flex-1 flex flex-col items-center justify-start w-full h-full px-[20vw] pb-[4vw] pt-[2vw]">
                <slot></slot>
            </div>
        </div>

        <!-- Pagination (fixed at absolute bottom) -->
        <div class="absolute bottom-[6%] left-1/2 -translate-x-1/2 w-full px-[18%]">
            <slot name="pagination"></slot>
        </div>
    </div>
</template>

<script setup lang="ts">
</script>
