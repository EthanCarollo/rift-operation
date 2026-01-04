<script setup lang="ts">
useSeoMeta({
    title: 'Accueil',
    description: 'Rift Hub - Central Command Interface'
})
</script>

<template>
    <div class="max-w-7xl mx-auto py-20 px-6">
        <!-- Hero -->
        <div class="text-center mb-24">
            <h1 class="text-6xl font-bold mb-6 tracking-tight">RIFT HUB</h1>
            <p class="text-xl text-text-sec max-w-2xl mx-auto">
                Interface centrale de commandement pour l'Opération Rift.
                Gérez les modules IoT, surveillez l'état de la faille et accédez aux archives.
            </p>
        </div>

        <!-- Navigation Cards -->
        <div class="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <!-- Studio Card -->
            <NuxtLink to="/studio"
                class="group p-8 border border-border bg-white hover:border-accent hover:shadow-lg transition-all duration-300 rounded-lg flex flex-col items-center text-center">
                <div
                    class="mb-6 mx-auto w-16 h-16 bg-bg-sec rounded-full flex items-center justify-center group-hover:bg-accent group-hover:text-accent-text transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                    </svg>
                </div>
                <h2 class="text-2xl font-bold mb-3 group-hover:text-accent">Studio</h2>
                <p class="text-text-sec text-sm">
                    Interface de contrôle direct pour les modules LED et les simulations de scénarios.
                </p>
                <span
                    class="mt-6 text-xs font-bold uppercase tracking-wider text-accent opacity-0 group-hover:opacity-100 transition-opacity">
                    Accéder au Studio →
                </span>
            </NuxtLink>

            <!-- Video Card -->
            <NuxtLink to="/video"
                class="group p-8 border border-border bg-white hover:border-accent hover:shadow-lg transition-all duration-300 rounded-lg flex flex-col items-center text-center">
                <div
                    class="mb-6 mx-auto w-16 h-16 bg-bg-sec rounded-full flex items-center justify-center group-hover:bg-accent group-hover:text-accent-text transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                </div>
                <h2 class="text-2xl font-bold mb-3 group-hover:text-accent">Projection</h2>
                <p class="text-text-sec text-sm">
                    Affichage principal pour le mapping vidéo et les retours visuels immersifs.
                </p>
                <span
                    class="mt-6 text-xs font-bold uppercase tracking-wider text-accent opacity-0 group-hover:opacity-100 transition-opacity">
                    Ouvrir la Projection →
                </span>
            </NuxtLink>

            <!-- Docs Card -->
            <NuxtLink to="/docs"
                class="group p-8 border border-border bg-white hover:border-accent hover:shadow-lg transition-all duration-300 rounded-lg flex flex-col items-center text-center">
                <div
                    class="mb-6 mx-auto w-16 h-16 bg-bg-sec rounded-full flex items-center justify-center group-hover:bg-accent group-hover:text-accent-text transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                </div>
                <h2 class="text-2xl font-bold mb-3 group-hover:text-accent">Documentation</h2>
                <p class="text-text-sec text-sm">
                    Guides techniques, protocoles JSON et manuels de référence pour l'Opération Rift.
                </p>
                <span
                    class="mt-6 text-xs font-bold uppercase tracking-wider text-accent opacity-0 group-hover:opacity-100 transition-opacity">
                    Consulter les Docs →
                </span>
            </NuxtLink>
        </div>
    </div>
</template>
