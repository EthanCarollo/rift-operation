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

        <!-- Camera Settings Panel -->
        <div class="mb-4 p-4 bg-neutral-800 rounded-lg border border-neutral-700">
            <div class="flex items-center justify-between mb-3">
                <h2 class="font-bold text-sm flex items-center gap-2">
                    <span class="text-blue-400">⚙️</span> Paramètres Caméra
                </h2>
                <button @click="resetCameraSettings"
                    class="px-3 py-1 text-xs bg-neutral-700 hover:bg-neutral-600 rounded transition-colors">
                    🔄 Reset
                </button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <!-- JPEG Quality -->
                <div class="space-y-2">
                    <div class="flex justify-between items-center">
                        <label class="text-xs text-neutral-400">Qualité JPEG</label>
                        <span class="text-xs font-mono bg-neutral-900 px-2 py-0.5 rounded">
                            {{ cameraSettings.jpeg_quality }}%
                        </span>
                    </div>
                    <input type="range" min="10" max="100" step="5" v-model.number="cameraSettings.jpeg_quality"
                        @input="debouncedUpdateSettings"
                        class="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-blue-500" />
                    <p class="text-xs text-neutral-500">↑ Plus haut = meilleure qualité, fichiers plus gros</p>
                </div>

                <!-- Denoise Strength -->
                <div class="space-y-2">
                    <div class="flex justify-between items-center">
                        <label class="text-xs text-neutral-400">Réduction Bruit</label>
                        <span class="text-xs font-mono bg-neutral-900 px-2 py-0.5 rounded"
                            :class="cameraSettings.denoise_strength > 0 ? 'text-green-400' : 'text-neutral-500'">
                            {{ cameraSettings.denoise_strength === 0 ? 'OFF' : cameraSettings.denoise_strength }}
                        </span>
                    </div>
                    <input type="range" min="0" max="10" step="1" v-model.number="cameraSettings.denoise_strength"
                        @input="debouncedUpdateSettings"
                        class="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-green-500" />
                    <p class="text-xs text-neutral-500">⚠️ Plus haut = plus lent mais moins de noise</p>
                </div>

                <!-- Resolution Scale -->
                <div class="space-y-2">
                    <div class="flex justify-between items-center">
                        <label class="text-xs text-neutral-400">Résolution</label>
                        <span class="text-xs font-mono bg-neutral-900 px-2 py-0.5 rounded">
                            {{ Math.round(cameraSettings.capture_scale * 100) }}%
                        </span>
                    </div>
                    <select v-model.number="cameraSettings.capture_scale" @change="updateCameraSettings"
                        class="w-full bg-neutral-700 border border-neutral-600 rounded px-2 py-1.5 text-xs">
                        <option :value="1.0">100% (Full HD)</option>
                        <option :value="0.75">75%</option>
                        <option :value="0.5">50%</option>
                        <option :value="0.25">25% (Rapide)</option>
                    </select>
                    <p class="text-xs text-neutral-500">↓ Plus bas = plus rapide, moins de détails</p>
                </div>
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

const config = useRuntimeConfig();
const backendUrl = ref(config.public.backendUrl);
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

// Camera compression settings
const cameraSettings = ref({
    jpeg_quality: 85,
    capture_scale: 1.0,
    denoise_strength: 0
});

let socket = null;
let updateSettingsTimeout = null;

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
            // Only log if the frame actually changed (new generation)
            const prevFrame = outputs.value[data.role];
            const isNewFrame = !prevFrame || prevFrame.substring(0, 100) !== data.frame.substring(0, 100);
            
            outputs.value[data.role] = data.frame;
            
            if (isNewFrame) {
                const label = status.value?.cameras?.[data.role]?.label || 'image';
                addLog(data.role, label);
            }
        }
    });

    // Listen for camera settings updates from other clients
    socket.on('camera_settings_updated', (data) => {
        cameraSettings.value = { ...cameraSettings.value, ...data };
    });
}

function updateCamera(role) {
    if (socket) {
        socket.emit('set_camera', { role, camera_index: selectedCameras.value[role] });
    }
}

// Camera settings functions
function updateCameraSettings() {
    if (socket) {
        socket.emit('update_camera_settings', cameraSettings.value);
    }
}

function debouncedUpdateSettings() {
    // Debounce slider changes to avoid spamming the server
    if (updateSettingsTimeout) {
        clearTimeout(updateSettingsTimeout);
    }
    updateSettingsTimeout = setTimeout(() => {
        updateCameraSettings();
    }, 100);
}

async function resetCameraSettings() {
    try {
        const res = await fetch(`${backendUrl.value}/camera_settings/reset`, {
            method: 'POST'
        });
        if (res.ok) {
            const data = await res.json();
            cameraSettings.value = data;
        }
    } catch (e) {
        console.error('[Config] Failed to reset camera settings:', e);
    }
}

async function fetchCameraSettings() {
    try {
        const res = await fetch(`${backendUrl.value}/camera_settings`);
        if (res.ok) {
            const data = await res.json();
            cameraSettings.value = data;
        }
    } catch (e) {
        console.error('[Config] Failed to fetch camera settings:', e);
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
    // backendUrl.value = `http://${window.location.hostname}:5010`; // Forced to 192.168.10.7
    connect();
    await fetchCameras();
    await fetchCameraSettings();
    setTimeout(() => {
        updateCamera('nightmare');
        updateCamera('dream');
    }, 1000);
});

onUnmounted(() => {
    if (socket) socket.disconnect();
    if (updateSettingsTimeout) clearTimeout(updateSettingsTimeout);
});
</script>
