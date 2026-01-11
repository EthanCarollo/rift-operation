<template>
    <div class="dev-panel" data-testid="dev-panel">
        <!-- Status Indicator -->
        <div class="status-indicator" data-testid="dev-status-indicator">
            <div class="status-dot-wrapper">
                <span v-if="isConnected" class="status-ping"></span>
                <span class="status-dot" :class="isConnected ? 'connected' : 'disconnected'"></span>
            </div>
            <span class="status-text">
                {{ isConnected ? (currentState !== 'inactive' ? currentState : 'ONLINE') : 'OFFLINE' }}
            </span>
        </div>

        <!-- Control Panel -->
        <div class="control-panel">
            <div class="panel-header">
                <span class="panel-title">Control Panel</span>
                <span class="panel-badge">DEV</span>
            </div>

            <!-- State buttons -->
            <div class="state-buttons">
                <button v-for="state in states" :key="state" @click="$emit('setState', state)" class="state-btn"
                    :class="{ active: currentState === state }">
                    {{ formatState(state) }}
                </button>
            </div>

            <!-- URL input -->
            <div class="url-section">
                <input :value="urlValue" @input="$emit('update:urlValue', ($event.target as HTMLInputElement).value)"
                    type="text" placeholder="ws://..." class="url-input" />
                <button @click="$emit('reconnect')" class="reconnect-btn">
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

<style scoped>
.dev-panel {
    position: fixed;
    bottom: 1.5rem;
    right: 1.5rem;
    z-index: 50;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    align-items: flex-end;
}

.status-indicator {
    background-color: rgba(21, 0, 89, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 0.5rem 1rem;
    border-radius: 9999px;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    backdrop-filter: blur(8px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}

.status-dot-wrapper {
    position: relative;
    display: flex;
    width: 12px;
    height: 12px;
}

.status-ping {
    position: absolute;
    inset: 0;
    border-radius: 9999px;
    background-color: #00FFC4;
    opacity: 0.75;
    animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.status-dot {
    position: relative;
    width: 12px;
    height: 12px;
    border-radius: 9999px;
}

.status-dot.connected {
    background-color: #00FFC4;
}

.status-dot.disconnected {
    background-color: #ef4444;
}

.status-text {
    font-size: 0.75rem;
    font-weight: bold;
    color: white;
    font-family: monospace;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.control-panel {
    background-color: rgba(15, 23, 42, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 1.25rem;
    border-radius: 1rem;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(8px);
    width: 280px;
    color: white;
}

.panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-title {
    font-weight: bold;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #9ca3af;
}

.panel-badge {
    font-size: 0.625rem;
    background-color: rgba(255, 255, 255, 0.1);
    padding: 0.125rem 0.5rem;
    border-radius: 0.25rem;
    color: #d1d5db;
}

.state-buttons {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.state-btn {
    padding: 0.375rem 0.5rem;
    font-size: 0.625rem;
    font-weight: bold;
    border-radius: 0.5rem;
    transition: all 0.2s;
    border: 1px solid;
    cursor: pointer;
    background-color: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.05);
    color: #9ca3af;
}

.state-btn:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
}

.state-btn.active {
    background-color: #FF00CF;
    border-color: #FF00CF;
    color: white;
}

.url-section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.url-input {
    width: 100%;
    background-color: #1e293b;
    color: #d1d5db;
    font-size: 0.75rem;
    padding: 0.625rem 0.75rem;
    border-radius: 0.5rem;
    border: 1px solid rgba(255, 255, 255, 0.05);
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.url-input:focus {
    border-color: rgba(255, 0, 207, 0.5);
    box-shadow: 0 0 0 2px rgba(255, 0, 207, 0.25);
}

.reconnect-btn {
    width: 100%;
    padding: 0.5rem;
    font-size: 0.75rem;
    font-weight: bold;
    color: #150059;
    background-color: #00FFC4;
    border-radius: 0.5rem;
    border: none;
    cursor: pointer;
    transition: background-color 0.2s;
}

.reconnect-btn:hover {
    background-color: rgba(0, 255, 196, 0.9);
}

@keyframes ping {

    75%,
    100% {
        transform: scale(2);
        opacity: 0;
    }
}
</style>
