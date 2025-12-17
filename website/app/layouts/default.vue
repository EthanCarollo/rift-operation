<template>
  <div class="min-h-screen bg-bg-main text-text-main font-mono transition-colors duration-300">
    <!-- Navigation -->
    <nav class="border-b border-border bg-bg-sec/50 backdrop-blur-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
        <!-- Brand -->
        <!-- Brand -->
        <NuxtLink to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <img src="/riftoperation.png" alt="Logo" class="h-8 w-auto filter grayscale opacity-80" />
          <span class="text-xl font-bold uppercase tracking-widest text-accent">Rift Hub</span>
        </NuxtLink>

        <!-- Links -->
        <div class="flex items-center gap-6">
          <NuxtLink to="/studio" class="text-xs font-bold uppercase tracking-wider hover:text-accent transition-colors"
            active-class="text-accent underline decoration-2 underline-offset-4">
            Studio
          </NuxtLink>
          <NuxtLink to="/docs" class="text-xs font-bold uppercase tracking-wider hover:text-accent transition-colors"
            active-class="text-accent underline decoration-2 underline-offset-4">
            Docs
          </NuxtLink>
          <span class="text-xs font-bold uppercase tracking-wider text-text-sec cursor-not-allowed opacity-50"
            title="Coming Soon">
            Dashboard
          </span>
          <span class="text-xs font-bold uppercase tracking-wider text-text-sec cursor-not-allowed opacity-50"
            title="Coming Soon">
            Settings
          </span>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main>
      <slot />
    </main>

    <!-- Footer -->
    <footer class="border-t border-border mt-20 py-8 text-center">
      <p class="text-[10px] uppercase text-text-sec tracking-widest">System Ready • v1.0.0</p>
    </footer>
  </div>
</template>
