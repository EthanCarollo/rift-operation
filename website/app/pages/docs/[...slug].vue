<script setup lang="ts">
const route = useRoute()
const { data: page } = await useAsyncData(route.path, () => {
    return queryCollection('docs').path(route.path).first()
})

useSeoMeta({
    title: page.value?.title,
    description: page.value?.description
})
</script>

<template>
    <div class="max-w-7xl mx-auto py-12 px-6">
        <div v-if="page" class="grid grid-cols-1 lg:grid-cols-4 gap-12">
            <!-- Sidebar (TOC) -->
            <aside class="hidden lg:block col-span-1">
                <div class="sticky top-24 space-y-8">
                    <div>
                        <NuxtLink to="/docs"
                            class="text-xs font-bold uppercase tracking-wider text-text-sec hover:text-accent transition-colors flex items-center gap-2 mb-6">
                            <span>←</span> Retour aux docs
                        </NuxtLink>
                    </div>

                    <div v-if="page.body?.toc?.links?.length">
                        <h3 class="text-xs font-bold uppercase tracking-wider text-text-sec mb-4">Dans cette page</h3>
                        <nav>
                            <ul class="space-y-2 text-sm">
                                <li v-for="link in page.body.toc.links" :key="link.id">
                                    <a :href="`#${link.id}`"
                                        class="block text-text-sec hover:text-accent transition-colors py-1">
                                        {{ link.text }}
                                    </a>
                                    <!-- Nested links (h3) -->
                                    <ul v-if="link.children" class="ml-4 mt-1 space-y-1 border-l border-border pl-4">
                                        <li v-for="child in link.children" :key="child.id">
                                            <a :href="`#${child.id}`"
                                                class="block text-text-sec hover:text-accent transition-colors py-1 text-xs">
                                                {{ child.text }}
                                            </a>
                                        </li>
                                    </ul>
                                </li>
                            </ul>
                        </nav>
                    </div>
                </div>
            </aside>

            <!-- Main Content -->
            <article class="col-span-1 lg:col-span-3">
                <!-- Mobile Back Button -->
                <div class="lg:hidden mb-8">
                    <NuxtLink to="/docs"
                        class="text-xs font-bold uppercase tracking-wider text-text-sec hover:text-accent transition-colors flex items-center gap-2">
                        <span>←</span> Retour aux docs
                    </NuxtLink>
                </div>

                <h1 class="text-4xl font-bold mb-4">{{ page.title }}</h1>
                <p class="text-xl text-text-sec mb-8">{{ page.description }}</p>

                <ContentRenderer :value="page" class="prose max-w-none prose-headings:scroll-mt-24" />
            </article>
        </div>

        <!-- 404 State -->
        <div v-else class="text-center py-20">
            <h1 class="text-2xl font-bold mb-4">Page not found</h1>
            <NuxtLink to="/docs" class="text-accent hover:underline">Go to Documentation</NuxtLink>
        </div>
    </div>
</template>
