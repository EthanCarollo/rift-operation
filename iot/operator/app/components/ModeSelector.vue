<template>
  <div class="flex flex-col items-center justify-center min-h-[60vh] p-4 font-mono">
    
    <div class="border border-[var(--border)] bg-[var(--bg-sec)] p-12 max-w-4xl w-full relative">
      <div class="absolute -top-3 left-4 bg-[var(--bg-main)] px-2 text-xs font-bold uppercase tracking-wider border border-[var(--border)] text-[var(--text-sec)]">
        00_System_Init
      </div>

      <h1 class="text-4xl font-bold mb-2 uppercase tracking-tight text-[var(--text-main)] text-center">
        Rift Operation
      </h1>
      <p class="text-[var(--text-sec)] text-center text-xs uppercase mb-12 tracking-widest">
        Select Operation Mode
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <!-- Dream Mode -->
        <button 
          @click="$emit('select', 'Dream')"
          class="group relative border border-[var(--border)] bg-[var(--bg-main)] p-8 transition-all duration-200 hover:-translate-y-1 hover:shadow-lg hover:border-[var(--border-focus)] text-left"
        >
          <div class="absolute top-4 right-4 text-[var(--text-sec)] text-xs font-bold font-mono group-hover:text-[var(--text-main)]">
            OPT_01
          </div>
          <div class="mb-4 text-4xl opacity-50 grayscale group-hover:grayscale-0 transition-all">
            🌙
          </div>
          <h2 class="text-xl font-bold uppercase mb-2 group-hover:underline decoration-1 underline-offset-4">Dream Mode</h2>
          <p class="text-[var(--text-sec)] text-xs font-mono leading-relaxed">
            Standard monitoring parameters.<br>Low latency.<br>Peaceful observation.
          </p>
        </button>

        <!-- Nightmare Mode -->
        <button 
          @click="$emit('select', 'Nightmare')"
          class="group relative border border-[var(--border)] bg-[var(--bg-main)] p-8 transition-all duration-200 hover:-translate-y-1 hover:shadow-lg hover:border-[var(--border-focus)] text-left"
        >
           <div class="absolute top-4 right-4 text-[var(--text-sec)] text-xs font-bold font-mono group-hover:text-[var(--text-main)]">
            OPT_02
          </div>
          <div class="mb-4 text-4xl opacity-50 grayscale group-hover:grayscale-0 transition-all">
            🔥
          </div>
          <h2 class="text-xl font-bold uppercase mb-2 group-hover:underline decoration-1 underline-offset-4">Nightmare Mode</h2>
          <p class="text-[var(--text-sec)] text-xs font-mono leading-relaxed">
            Critical response protocols.<br>High alert status.<br>Active surveillance.
          </p>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  (e: 'select', mode: 'Dream' | 'Nightmare'): void
}>()
</script>
