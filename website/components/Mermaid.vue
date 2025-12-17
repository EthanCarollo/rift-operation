<script setup lang="ts">
import mermaid from 'mermaid'

const props = defineProps({
    code: {
        type: String,
        required: true
    }
})

const container = ref<HTMLElement | null>(null)

// Initialize mermaid
mermaid.initialize({
    startOnLoad: false,
    theme: 'base',
    themeVariables: {
        fontFamily: '"Space Mono", monospace',
        primaryColor: '#f4f4f5',
        primaryTextColor: '#18181b',
        primaryBorderColor: '#18181b',
        lineColor: '#18181b',
        secondaryColor: '#ffffff',
        tertiaryColor: '#ffffff'
    }
})

onMounted(async () => {
    await renderDiagram()
})

watch(() => props.code, () => {
    renderDiagram()
})

const renderDiagram = async () => {
    if (!container.value) return

    const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`

    try {
        const { svg } = await mermaid.render(id, props.code)
        container.value.innerHTML = svg
    } catch (error) {
        console.error('Mermaid render error:', error)
        if (container.value) {
            container.value.innerHTML = `<pre class="text-red-500 text-xs p-4 border border-red-200 bg-red-50 rounded">${error}</pre>`
        }
    }
}
</script>

<template>
    <div ref="container"
        class="mermaid-diagram my-8 overflow-x-auto p-4 bg-white border border-border rounded flex justify-center">
        <!-- SVG rendered here -->
    </div>
</template>
