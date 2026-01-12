<template>
    <div class="fixed bottom-6 right-6 z-50 flex flex-col gap-3 items-end" data-testid="dev-panel">
        <!-- Status Indicator -->
        <div class="bg-stranger-blue/80 border border-white/20 px-4 py-2 rounded-full flex items-center gap-3 backdrop-blur-md shadow-lg"
            data-testid="dev-status-indicator">
            <div class="relative flex w-3 h-3">
                <span v-if="isConnected"
                    class="absolute inset-0 rounded-full bg-stranger-green opacity-75 animate-ping"></span>
                <span class="relative w-3 h-3 rounded-full"
                    :class="isConnected ? 'bg-stranger-green' : 'bg-red-500'"></span>
            </div>
            <span class="text-xs font-bold text-white font-mono tracking-widest uppercase">
                {{ isConnected ? (currentState !== 'inactive' ? currentState : 'ONLINE') : 'OFFLINE' }}
            </span>
        </div>

        <!-- Control Panel -->
        <div class="bg-slate-900/95 border border-white/10 p-5 rounded-2xl shadow-2xl backdrop-blur-md w-72 text-white">
            <div class="flex items-center justify-between mb-4 pb-2 border-b border-white/10">
                <span class="font-bold text-xs uppercase tracking-widest text-gray-400">Control Panel</span>
                <span class="text-[10px] bg-white/10 px-2 py-0.5 rounded text-gray-300">DEV</span>
            </div>

            <!-- State buttons -->
            <div class="grid grid-cols-3 gap-2 mb-4">
                <button v-for="state in states" :key="state" @click="$emit('setState', state)"
                    class="px-2 py-1.5 text-[10px] font-bold rounded-lg transition-all duration-200 border cursor-pointer"
                    :class="currentState === state
                        ? 'bg-stranger-rose border-stranger-rose text-white'
                        : 'bg-white/5 border-white/5 text-gray-400 hover:bg-white/10 hover:text-white'">
                    {{ formatState(state) }}
                </button>
            </div>

            <!-- URL input -->
            <div class="flex flex-col gap-2">
                <input :value="urlValue" @input="$emit('update:urlValue', ($event.target as HTMLInputElement).value)"
                    type="text" placeholder="ws://..."
                    class="w-full bg-slate-800 text-gray-300 text-xs px-3 py-2.5 rounded-lg border border-white/5 outline-none focus:border-stranger-rose/50 focus:ring-1 focus:ring-stranger-rose/50 transition-all" />
                <button @click="$emit('reconnect')"
                    class="w-full py-2 text-xs font-bold text-stranger-blue bg-stranger-green rounded-lg hover:bg-stranger-green/90 transition-all cursor-pointer">
                    UPDATE CONNECTION
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
interface Props {
    isConnected: boolean
    currentState: string
    states: string[]
    urlValue: string
}

defineProps<Props>()

defineEmits<{
    setState: [state: string]
    reconnect: []
    'update:urlValue': [value: string]
}>()

const formatState = (state: string): string => {
    return state.replace('step_', 'S').toUpperCase()
}
</script>
