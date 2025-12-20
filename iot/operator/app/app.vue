<template>
  <div v-if="route.name !== 'monitor'" class="fixed top-0 left-0 bg-red-600 text-white px-3 py-1.5 text-sm font-bold z-50 pointer-events-none">DEV</div>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup lang="ts">
import '~/assets/css/main.css'
const route = useRoute()
</script>
