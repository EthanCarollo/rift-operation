<script setup lang="ts">
const { data: docs } = await useAsyncData('docs-list', () => {
    return queryCollection('docs').all()
})

const categories = computed(() => {
    if (!docs.value) return []
    const cats = docs.value.map(doc => doc.category || 'General')
    return [...new Set(cats)].sort()
})

const selectedCategory = ref('All')

const filteredDocs = computed(() => {
    if (!docs.value) return []
    if (selectedCategory.value === 'All') return docs.value
    return docs.value.filter(doc => (doc.category || 'General') === selectedCategory.value)
})

useSeoMeta({
    title: 'Documentation',
    description: 'Rift Hub Documentation'
})
</script>

<template>
    <div class="max-w-4xl mx-auto py-12 px-6">
        <div class="mb-12 border-b border-border pb-8">
            <h1 class="text-4xl font-bold mb-4">Documentation</h1>
            <p class="text-text-sec text-lg">Guides et références pour les outils Rift Operation.</p>

            <!-- Filters -->
            <div class="flex flex-wrap gap-2 mt-8">
                <button @click="selectedCategory = 'All'"
                    class="px-4 py-2 text-xs font-bold uppercase tracking-wider rounded-full transition-colors border"
                    :class="selectedCategory === 'All' ? 'bg-accent text-accent-text border-accent' : 'bg-transparent text-text-sec border-border hover:border-accent hover:text-text-main'">
                    Tous
                </button>
                <button v-for="cat in categories" :key="cat" @click="selectedCategory = cat"
                    class="px-4 py-2 text-xs font-bold uppercase tracking-wider rounded-full transition-colors border"
                    :class="selectedCategory === cat ? 'bg-accent text-accent-text border-accent' : 'bg-transparent text-text-sec border-border hover:border-accent hover:text-text-main'">
                    {{ cat }}
                </button>
            </div>
        </div>

        <div class="grid gap-6 md:grid-cols-2">
            <NuxtLink v-for="doc in filteredDocs" :key="doc.path" :to="doc.path"
                class="group block p-6 border border-border bg-white hover:border-accent transition-colors duration-200 flex flex-col h-full">
                <div class="flex-grow">
                    <span
                        class="inline-block px-2 py-1 mb-3 text-[10px] font-bold uppercase tracking-widest border border-border rounded text-text-sec">
                        {{ doc.category || 'General' }}
                    </span>
                    <h2 class="text-xl font-bold mb-2 group-hover:text-accent transition-colors">{{ doc.title }}</h2>
                    <p class="text-sm text-text-sec line-clamp-2 mb-3">{{ doc.description || 'Aucune description disponible.'
                    }}</p>
                    <div v-if="doc.tags && doc.tags.length > 0" class="flex flex-wrap gap-1">
                        <span v-for="tag in doc.tags" :key="tag" 
                              class="px-1.5 py-0.5 text-[10px] bg-gray-100 text-gray-600 rounded border border-gray-200">
                            #{{ tag }}
                        </span>
                    </div>
                </div>
                <div
                    class="mt-4 flex items-center text-xs font-bold uppercase tracking-wider text-accent opacity-0 group-hover:opacity-100 transition-opacity">
                    Lire le guide <span class="ml-2">→</span>
                </div>
            </NuxtLink>
        </div>
    </div>
</template>
