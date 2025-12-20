<template>
  <div
    class="h-screen w-screen bg-bg-main text-text-main overflow-hidden flex flex-col font-mono relative transition-colors duration-300">

    <!-- DEV Badge -->
    <div
      class="fixed top-0 left-0 bg-red-600 text-white px-3 py-1.5 text-sm font-bold z-50 pointer-events-none select-none shadow-sm">
      DEV
    </div>

    <!-- Top Bar (Toolbar placeholder) -->
    <header class="h-10 bg-bg-sec border-b border-border flex items-center px-4 pl-16 gap-4 select-none">
      <h1 class="text-xs font-bold text-text-sec tracking-widest uppercase">Sound Monitor // Operator</h1>
      <div class="flex-1"></div>
      <div class="h-6 px-3 bg-bg-main flex items-center justify-center text-[10px] text-success border border-border">
        CPU: 12%
      </div>
      <div
        class="h-6 px-3 bg-bg-main flex items-center justify-center text-[10px] text-orange-500 border border-border">
        MEM: 480MB
      </div>
    </header>

    <!-- Main Mixer Area -->
    <main class="flex-1 flex overflow-x-auto overflow-y-hidden bg-bg-sec/50 p-4 relative justify-center">

      <!-- Mixer Container -->
      <div class="flex h-full shadow-lg border border-border bg-bg-main relative">

        <AudioBus v-for="(bus, index) in buses" :key="bus.id" :bus-name="bus.name" :bus-id="bus.id"
          :devices="audioDevices" :class="{ 'border-l': index !== 0, 'border-border': true }" />

      </div>

    </main>

    <!-- Status Bar -->
    <footer class="h-6 bg-bg-sec border-t border-border flex items-center px-2 text-[9px] text-text-sec">
      <span>READY</span>
      <span class="mx-2">|</span>
      <span>44.1kHz</span>
    </footer>

  </div>
</template>

<script setup lang="ts">
import AudioBus from './components/AudioBus.vue';

// Buses Configuration
const buses = ref([
  { id: 1, name: 'Nightmare' },
  { id: 2, name: 'Dream' },
  { id: 3, name: 'Rift' },
  { id: 4, name: 'SAS / OPERATOR' },
]);

const audioDevices = ref([
  { id: 'dev1', name: 'Built-in Output' },
  { id: 'dev2', name: 'Scarlett 2i2' },
  { id: 'dev3', name: 'Virtual Cable 1' },
  { id: 'dev4', name: 'HDMI Audio' },
]);
</script>

<style>
/* Global scrollbar for the mixer horizontal scroll */
::-webkit-scrollbar {
  height: 8px;
  width: 8px;
  background: var(--bg-sec);
}

::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-sec);
}

html,
body {
  overscroll-behavior: none;
  margin: 0;
  padding: 0;
  /* Ensure light theme by default */
  background-color: var(--bg-main);
}
</style>
