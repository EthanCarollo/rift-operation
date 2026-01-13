<template>
    <div class="min-h-screen bg-neutral-900 text-neutral-200 p-4 font-mono text-sm">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4 border-b border-neutral-700 pb-3">
            <h1 class="text-lg font-bold">Battle Camera Config</h1>
            <div class="flex items-center gap-4">
                <span class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full" :class="connected ? 'bg-green-500' : 'bg-red-500'"></span>
                    {{ connected ? 'Connected' : 'Offline' }}
                </span>
                <NuxtLink to="/" class="px-3 py-1 border border-neutral-600 rounded hover:bg-neutral-800">
                    ← Battle
                </NuxtLink>
            </div>
        </div>

        <!-- Status Bar -->
        <div class="flex gap-4 mb-4 text-xs">
            <div class="flex gap-2">
                <span class="text-neutral-500">STATE:</span>
                <span class="font-bold">{{ status?.ws_state?.battle_state || 'IDLE' }}</span>
            </div>
            <div class="flex gap-2">
                <span class="text-neutral-500">ATTACK:</span>
                <span class="font-bold text-yellow-400">{{ status?.current_attack || '—' }}</span>
            </div>
            <div class="flex gap-2">
                <span class="text-neutral-500">WS:</span>
                <span :class="status?.ws_connected ? 'text-green-400' : 'text-neutral-500'">
                    {{ status?.ws_connected ? 'OK' : 'OFF' }}
                </span>
            </div>
            <div class="flex gap-2">
                <span class="text-neutral-500">RUNNING:</span>
                <span :class="status?.running ? 'text-green-400' : 'text-neutral-500'">
                    {{ status?.running ? 'YES' : 'NO' }}
                </span>
            </div>
        </div>

        <!-- All States Debug -->
        <details class="mb-4">
            <summary class="cursor-pointer text-neutral-500 hover:text-neutral-300 text-xs">
                [DEBUG] Full WS State
            </summary>
            <pre class="mt-2 p-2 bg-neutral-800 rounded text-xs overflow-auto max-h-32">{{ JSON.stringify(status?.ws_state, null, 2) }}</pre>
        </details>

        <!-- Grid: 2 columns for cameras -->
        <div class="grid grid-cols-2 gap-4">
            <!-- Nightmare Column -->
            <div class="space-y-2">
                <div class="flex items-center justify-between">
                    <span class="font-bold">NIGHTMARE</span>
                    <select v-model="selectedCameras.nightmare" @change="updateCamera('nightmare')"
                        class="bg-neutral-800 border border-neutral-700 rounded px-2 py-1 text-xs">
                        <option v-for="cam in cameras" :key="cam.index" :value="cam.index">
                            {{ cam.index }}: {{ cam.name }}
                        </option>
                    </select>
                </div>
                
                <!-- Camera Feed + Output Overlay -->
                <div class="relative aspect-video bg-black rounded overflow-hidden border border-neutral-700">
                    <!-- Camera Feed (background) -->
                    <img v-if="frames.nightmare" :src="'data:image/jpeg;base64,' + frames.nightmare"
                        class="absolute inset-0 w-full h-full object-cover" alt="Nightmare Camera" />
                    <div v-else class="absolute inset-0 w-full h-full flex items-center justify-center text-neutral-600">
                        No Feed
                    </div>
                    
                    <!-- Output overlay -->
                    <img v-if="outputs.nightmare" :src="'data:image/png;base64,' + outputs.nightmare"
                        class="absolute inset-0 w-full h-full object-contain z-10" alt="Output" />
                </div>

                <div class="text-xs text-neutral-500">
                    {{ recognition.nightmare || 'Idle' }}
                </div>
            </div>

            <!-- Dream Column -->
            <div class="space-y-2">
                <div class="flex items-center justify-between">
                    <span class="font-bold">DREAM</span>
                    <select v-model="selectedCameras.dream" @change="updateCamera('dream')"
                        class="bg-neutral-800 border border-neutral-700 rounded px-2 py-1 text-xs">
                        <option v-for="cam in cameras" :key="cam.index" :value="cam.index">
                            {{ cam.index }}: {{ cam.name }}
                        </option>
                    </select>
                </div>
                
                <!-- Camera Feed + Output Overlay -->
                <div class="relative aspect-video bg-black rounded overflow-hidden border border-neutral-700">
                    <!-- Camera Feed (background) -->
                    <img v-if="frames.dream" :src="'data:image/jpeg;base64,' + frames.dream"
                        class="absolute inset-0 w-full h-full object-cover" alt="Dream Camera" />
                    <div v-else class="absolute inset-0 w-full h-full flex items-center justify-center text-neutral-600">
                        No Feed
                    </div>
                    
                    <!-- Output overlay -->
                    <img v-if="outputs.dream" :src="'data:image/png;base64,' + outputs.dream"
                        class="absolute inset-0 w-full h-full object-contain z-10" alt="Output" />
                </div>

                <div class="text-xs text-neutral-500">
                    {{ recognition.dream || 'Idle' }}
                </div>
            </div>
        </div> <!-- End Grid -->

        <!-- Logs Section -->
        <div class="mt-4 border-t border-neutral-700 pt-4">
            <h2 class="text-xs font-bold mb-2 text-neutral-400">ACTIVITY LOG</h2>
            <div class="h-32 overflow-y-auto bg-neutral-800 rounded p-2 text-xs font-mono space-y-1">
                <div v-for="(log, i) in logs" :key="i" class="text-neutral-400">
                    <span class="text-neutral-600">[{{ log.time }}]</span>
                    <span :class="log.role === 'dream' ? 'text-blue-400' : 'text-pink-400'">{{ log.role.toUpperCase() }}</span>
                    <span>: generated </span>
                    <span class="text-white">{{ log.label || 'unknown' }}</span>
                </div>
                <div v-if="logs.length === 0" class="text-neutral-600 italic">No activity yet...</div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { io } from 'socket.io-client';

const backendUrl = ref('http://localhost:5010');
const connected = ref(false);
const status = ref(null);
const logs = ref([]);
const cameras = ref([
    { index: 0, name: 'Camera 0' },
    { index: 1, name: 'Camera 1' }
]);
const selectedCameras = ref({ nightmare: 0, dream: 1 });
const frames = ref({ nightmare: null, dream: null });
const outputs = ref({ nightmare: null, dream: null });
const recognition = ref({ nightmare: '', dream: '' });

let socket = null;

function addLog(role, label) {
    const time = new Date().toLocaleTimeString();
    logs.value.unshift({ time, role, label });
    if (logs.value.length > 50) logs.value.pop();
}

function connect() {
    socket = io(backendUrl.value, { transports: ['websocket', 'polling'] });

    socket.on('connect', () => {
        connected.value = true;
        console.log('[Config] Connected');
    });

    socket.on('disconnect', () => {
        connected.value = false;
    });

    socket.on('status', (data) => {
        status.value = data;
    });

    socket.on('camera_frame', (data) => {
        if (data.role && data.frame) {
            frames.value[data.role] = data.frame;
            if (data.recognition) {
                recognition.value[data.role] = data.recognition;
            }
        }
    });

    socket.on('output_frame', (data) => {
        if (data.role && data.frame) {
            outputs.value[data.role] = data.frame;
            
            // Log this event
            // Try to find the label from status if available, or just log generation
            const label = status.value?.cameras?.[data.role]?.label || 'image';
            addLog(data.role, label);
        }
    });
}

function updateCamera(role) {
    if (socket) {
        socket.emit('set_camera', { role, camera_index: selectedCameras.value[role] });
    }
}

async function fetchCameras() {
    try {
        const res = await fetch(`${backendUrl.value}/cameras`);
        if (res.ok) cameras.value = await res.json();
    } catch (e) {
        console.error('[Config] Failed to fetch cameras:', e);
    }
}

onMounted(async () => {
    backendUrl.value = `http://${window.location.hostname}:5010`;
    connect();
    await fetchCameras();
    setTimeout(() => {
        updateCamera('nightmare');
        updateCamera('dream');
    }, 1000);
});

onUnmounted(() => {
    if (socket) socket.disconnect();
});
</script>
