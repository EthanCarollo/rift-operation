<script setup lang="ts">
const props = defineProps({
    code: {
        type: String,
        default: ''
    },
    language: {
        type: String,
        default: null
    },
    filename: {
        type: String,
        default: null
    },
    highlights: {
        type: Array as () => number[],
        default: () => []
    },
    meta: {
        type: String,
        default: null
    },
    class: {
        type: String,
        default: null
    }
})

import Mermaid from './Mermaid.vue'

onMounted(() => {
    if (props.language === 'mermaid') {
        console.log('Found mermaid block', props.code)
    }
})
</script>

<template>
    <Mermaid v-if="language === 'mermaid'" :code="code" />
    <pre v-else :class="$props.class"><slot /></pre>
</template>
