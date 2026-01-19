<template>
    <div class="min-h-screen bg-neutral-900 text-neutral-200 p-4 font-mono text-sm">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4 border-b border-neutral-700 pb-3">
            <h1 class="text-lg font-bold">Battle Camera Controller (Remote)</h1>
            <div class="flex items-center gap-4">
                <span class="flex items-center gap-2 text-xs">
                    <span class="w-2 h-2 rounded-full" :class="connected ? 'bg-green-500' : 'bg-red-500'"></span>
                    {{ connected ? 'Connected' : 'Offline' }}
                </span>
                <NuxtLink to="/train" class="px-3 py-1 border border-green-600 text-green-400 rounded hover:bg-green-900/30">
                    🧠 Train KNN
                </NuxtLink>
                <NuxtLink to="/" class="px-3 py-1 border border-neutral-600 rounded hover:bg-neutral-800">
                    ← Battle
                </NuxtLink>
            </div>
        </div>

        <div class="grid grid-cols-2 gap-8">
            <!-- Nightmare Config -->
            <div class="space-y-4">
                <h2 class="font-bold text-red-500 text-lg border-b border-red-900/30 pb-2">NIGHTMARE CAM</h2>
                
                <div class="bg-neutral-800 p-3 rounded space-y-2">
                    <label class="text-xs text-neutral-400">Remote Camera Source</label>
                    <select v-model="assignments.nightmare" @change="assignDevice('nightmare')"
                        class="w-full bg-neutral-900 border border-neutral-700 rounded p-2 text-white">
                        <option :value="null">-- No Camera --</option>
                        <option v-for="device in remoteDevices" :key="device.deviceId" :value="device.deviceId">
                            {{ device.label || 'Unknown Device' }}
                        </option>
                    </select>
                </div>

                <!-- Camera Preview (Raw Feed) -->
                <div class="relative aspect-video bg-neutral-950 rounded border border-neutral-800 overflow-hidden">
                     <img v-if="cameraPreviews.nightmare" :src="'data:image/jpeg;base64,' + cameraPreviews.nightmare"
                        class="absolute inset-0 w-full h-full object-cover" />
                     <div v-else class="absolute inset-0 flex items-center justify-center text-neutral-600 text-xs">
                        📷 No camera feed...
                     </div>
                     <div class="absolute top-2 left-2 bg-black/50 px-2 py-1 rounded text-xs">Live Camera</div>
                     <!-- KNN Status -->
                     <div v-if="knnStatus.nightmare" class="absolute bottom-2 left-2 right-2 bg-black/70 px-2 py-1 rounded text-xs">
                        🧠 KNN: <span class="font-bold" :class="knnStatus.nightmare.label === 'Need Training' ? 'text-yellow-400' : 'text-green-400'">{{ knnStatus.nightmare.label }}</span>
                        <span class="text-neutral-500 ml-1">({{ knnStatus.nightmare.distance?.toFixed(1) || '?' }})</span>
                     </div>
                </div>

                <!-- AI Output Preview (from Backend) -->
                <div class="relative aspect-video bg-black rounded border border-neutral-800 overflow-hidden group">
                     <img v-if="outputs.nightmare" :src="'data:image/png;base64,' + outputs.nightmare"
                        class="absolute inset-0 w-full h-full object-contain" />
                     <div v-else class="absolute inset-0 flex items-center justify-center text-neutral-600 text-xs">
                        🎨 Waiting for AI Output...
                     </div>
                     <div class="absolute top-2 left-2 bg-black/50 px-2 py-1 rounded text-xs">AI Output</div>
                </div>
            </div>

            <!-- Dream Config -->
            <div class="space-y-4">
                <h2 class="font-bold text-blue-500 text-lg border-b border-blue-900/30 pb-2">DREAM CAM</h2>
                
                <div class="bg-neutral-800 p-3 rounded space-y-2">
                    <label class="text-xs text-neutral-400">Remote Camera Source</label>
                    <select v-model="assignments.dream" @change="assignDevice('dream')"
                        class="w-full bg-neutral-900 border border-neutral-700 rounded p-2 text-white">
                        <option :value="null">-- No Camera --</option>
                        <option v-for="device in remoteDevices" :key="device.deviceId" :value="device.deviceId">
                            {{ device.label || 'Unknown Device' }}
                        </option>
                    </select>
                </div>

                <!-- Camera Preview (Raw Feed) -->
                <div class="relative aspect-video bg-neutral-950 rounded border border-neutral-800 overflow-hidden">
                     <img v-if="cameraPreviews.dream" :src="'data:image/jpeg;base64,' + cameraPreviews.dream"
                        class="absolute inset-0 w-full h-full object-cover" />
                     <div v-else class="absolute inset-0 flex items-center justify-center text-neutral-600 text-xs">
                        📷 No camera feed...
                     </div>
                     <div class="absolute top-2 left-2 bg-black/50 px-2 py-1 rounded text-xs">Live Camera</div>
                     <!-- KNN Status -->
                     <div v-if="knnStatus.dream" class="absolute bottom-2 left-2 right-2 bg-black/70 px-2 py-1 rounded text-xs">
                        🧠 KNN: <span class="font-bold" :class="knnStatus.dream.label === 'Need Training' ? 'text-yellow-400' : 'text-green-400'">{{ knnStatus.dream.label }}</span>
                        <span class="text-neutral-500 ml-1">({{ knnStatus.dream.distance?.toFixed(1) || '?' }})</span>
                     </div>
                </div>

                <!-- AI Output Preview (from Backend) -->
                <div class="relative aspect-video bg-black rounded border border-neutral-800 overflow-hidden group">
                     <img v-if="outputs.dream" :src="'data:image/png;base64,' + outputs.dream"
                        class="absolute inset-0 w-full h-full object-contain" />
                     <div v-else class="absolute inset-0 flex items-center justify-center text-neutral-600 text-xs">
                        🎨 Waiting for AI Output...
                     </div>
                     <div class="absolute top-2 left-2 bg-black/50 px-2 py-1 rounded text-xs">AI Output</div>
                </div>
            </div>
        </div>

        <!-- Debug Mode Toggle -->
        <div class="mt-8 p-4 bg-neutral-800 rounded border border-neutral-700">
            <label class="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" v-model="debugMode" @change="saveDebugMode"
                    class="w-5 h-5 rounded bg-neutral-900 border-neutral-600 text-purple-500 focus:ring-purple-500" />
                <div>
                    <span class="font-bold text-white">Debug Mode</span>
                    <p class="text-xs text-neutral-500">Show cameras on battle screens even when in IDLE state</p>
                </div>
            </label>
        </div>

        <div class="mt-4 p-4 bg-neutral-800/50 rounded text-center text-neutral-500 text-xs">
            <p>This page controls the cameras on the remote Battle Machine.</p>
            <p>Ensure the Battle Machine is running and connected (check logs for 'Client registered').</p>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { io } from 'socket.io-client';

const config = useRuntimeConfig();
const backendUrl = ref(config.public.backendUrl); // Forced to 192.168.10.7 via .env usually
const connected = ref(false);

const remoteDevices = ref([]);
const assignments = ref({ nightmare: null, dream: null });
const outputs = ref({ nightmare: null, dream: null });
const cameraPreviews = ref({ nightmare: null, dream: null });
const knnStatus = ref({
    nightmare: { label: 'Waiting...', distance: 0 },
    dream: { label: 'Waiting...', distance: 0 }
});
const debugMode = ref(false);

let socket = null;

function saveDebugMode() {
    socket.emit('set_debug_mode', { enabled: debugMode.value });
    console.log('[Config] Debug mode:', debugMode.value);
}

function connect() {
    socket = io(backendUrl.value, { transports: ['websocket', 'polling'] });

    socket.on('connect', () => {
        connected.value = true;
        console.log('[Config] Connected to Backend');
        
        // Request initial data
        fetchRemoteDevices();
        fetchAssignments();
        fetchDebugMode();
    });

    socket.on('disconnect', () => {
        connected.value = false;
    });

    // Listen for device list updates
    socket.on('remote_devices_update', (devices) => {
        console.log('[Config] Received devices update:', devices);
        remoteDevices.value = devices;
    });

    // Listen for AI output frames (to verify it works)
    socket.on('output_frame', (data) => {
        if (data.role && data.frame) {
            console.log(`[Config] 🎨 AI Output received for ${data.role.toUpperCase()} (${Math.round(data.frame.length / 1024)}KB)`);
            outputs.value[data.role] = data.frame;
        }
    });

    // Listen for status updates (generation progress)
    socket.on('status', (data) => {
        console.log('[Config] 📊 Status update:', JSON.stringify({
            attack: data.current_attack,
            dream: data.cameras?.dream,
            nightmare: data.cameras?.nightmare
        }, null, 2));

        if (data.cameras) {
            if (data.cameras.nightmare) {
                knnStatus.value.nightmare = {
                    label: data.cameras.nightmare.knn_label || 'Need Training',
                    distance: data.cameras.nightmare.knn_distance || 0
                };
            }
            if (data.cameras.dream) {
                knnStatus.value.dream = {
                    label: data.cameras.dream.knn_label || 'Need Training',
                    distance: data.cameras.dream.knn_distance || 0
                };
            }
        }
    });

    // Listen for camera preview frames
    socket.on('camera_preview', (data) => {
        if (data.role && data.frame) {
            cameraPreviews.value[data.role] = data.frame;
        }
    });
}

function assignDevice(role) {
    const deviceId = assignments.value[role];
    console.log(`[Config] Assigning ${role} -> ${deviceId}`);
    socket.emit('assign_device', { role, deviceId });
}

async function fetchRemoteDevices() {
    try {
        const res = await fetch(`${backendUrl.value}/remote/devices`);
        if (res.ok) {
            remoteDevices.value = await res.json();
        }
    } catch (e) {
        console.error('Failed to fetch remote devices:', e);
    }
}

async function fetchAssignments() {
    try {
        const res = await fetch(`${backendUrl.value}/remote/assignments`);
        if (res.ok) {
            const data = await res.json();
            if (data.nightmare) assignments.value.nightmare = data.nightmare;
            if (data.dream) assignments.value.dream = data.dream;
        }
    } catch (e) {
        console.error('Failed to fetch assignments:', e);
    }
}

async function fetchDebugMode() {
    try {
        const res = await fetch(`${backendUrl.value}/remote/debug_mode`);
        if (res.ok) {
            const data = await res.json();
            debugMode.value = data.debug_mode || false;
        }
    } catch (e) {
        console.error('Failed to fetch debug mode:', e);
    }
}

onMounted(() => {
    // Load debug mode
    const savedDebug = localStorage.getItem('battle_debug_mode');
    if (savedDebug) {
        try { debugMode.value = JSON.parse(savedDebug); } catch {}
    }
    
    connect();
});

onUnmounted(() => {
    if (socket) socket.disconnect();
});
</script>
