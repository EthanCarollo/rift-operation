<template>
    <div class="min-h-screen bg-gray-900 text-white p-8">
        <div class="max-w-6xl mx-auto">
            <!-- Header -->
            <div class="flex items-center justify-between mb-8">
                <h1 class="text-3xl font-bold text-purple-400">⚙️ Battle Camera Config</h1>
                <div class="flex items-center gap-4">
                    <span :class="connected ? 'text-green-400' : 'text-red-400'" class="flex items-center gap-2">
                        <span class="w-3 h-3 rounded-full" :class="connected ? 'bg-green-400' : 'bg-red-400'"></span>
                        {{ connected ? 'Connected' : 'Disconnected' }}
                    </span>
                    <NuxtLink to="/" class="px-4 py-2 bg-gray-700 rounded hover:bg-gray-600">
                        ← Back to Battle
                    </NuxtLink>
                </div>
            </div>

            <!-- Status Panel -->
            <div class="bg-gray-800 rounded-lg p-6 mb-8">
                <h2 class="text-xl font-semibold mb-4 text-blue-400">📊 Battle Status</h2>
                <div class="grid grid-cols-3 gap-4">
                    <div class="bg-gray-700 p-4 rounded">
                        <div class="text-gray-400 text-sm">State</div>
                        <div class="text-lg font-bold">{{ status?.ws_state?.battle_state || 'IDLE' }}</div>
                    </div>
                    <div class="bg-gray-700 p-4 rounded">
                        <div class="text-gray-400 text-sm">Current Attack</div>
                        <div class="text-lg font-bold">{{ status?.current_attack || 'None' }}</div>
                    </div>
                    <div class="bg-gray-700 p-4 rounded">
                        <div class="text-gray-400 text-sm">Running</div>
                        <div class="text-lg font-bold" :class="status?.running ? 'text-green-400' : 'text-gray-500'">
                            {{ status?.running ? 'Yes' : 'No' }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Camera Selection -->
            <div class="grid grid-cols-2 gap-8 mb-8">
                <!-- Nightmare Camera -->
                <div class="bg-gray-800 rounded-lg p-6">
                    <h2 class="text-xl font-semibold mb-4 text-pink-400">🌙 Nightmare Camera</h2>
                    <select v-model="selectedCameras.nightmare" @change="updateCamera('nightmare')"
                        class="w-full bg-gray-700 border border-gray-600 rounded p-3 mb-4">
                        <option v-for="cam in cameras" :key="cam.index" :value="cam.index">
                            {{ cam.index }}: {{ cam.name }}
                        </option>
                    </select>

                    <!-- Camera Preview -->
                    <div class="aspect-video bg-black rounded overflow-hidden">
                        <img v-if="frames.nightmare" :src="'data:image/jpeg;base64,' + frames.nightmare"
                            class="w-full h-full object-cover" alt="Nightmare Camera" />
                        <div v-else class="w-full h-full flex items-center justify-center text-gray-500">
                            No Feed
                        </div>
                    </div>

                    <!-- Recognition Status -->
                    <div class="mt-4 text-sm text-gray-400">
                        {{ recognition.nightmare || 'Waiting...' }}
                    </div>
                </div>

                <!-- Dream Camera -->
                <div class="bg-gray-800 rounded-lg p-6">
                    <h2 class="text-xl font-semibold mb-4 text-blue-400">☀️ Dream Camera</h2>
                    <select v-model="selectedCameras.dream" @change="updateCamera('dream')"
                        class="w-full bg-gray-700 border border-gray-600 rounded p-3 mb-4">
                        <option v-for="cam in cameras" :key="cam.index" :value="cam.index">
                            {{ cam.index }}: {{ cam.name }}
                        </option>
                    </select>

                    <!-- Camera Preview -->
                    <div class="aspect-video bg-black rounded overflow-hidden">
                        <img v-if="frames.dream" :src="'data:image/jpeg;base64,' + frames.dream"
                            class="w-full h-full object-cover" alt="Dream Camera" />
                        <div v-else class="w-full h-full flex items-center justify-center text-gray-500">
                            No Feed
                        </div>
                    </div>

                    <!-- Recognition Status -->
                    <div class="mt-4 text-sm text-gray-400">
                        {{ recognition.dream || 'Waiting...' }}
                    </div>
                </div>
            </div>

            <!-- Output Preview -->
            <div class="grid grid-cols-2 gap-8">
                <div class="bg-gray-800 rounded-lg p-6">
                    <h3 class="text-lg font-semibold mb-4 text-pink-400">🎨 Nightmare Output</h3>
                    <div class="aspect-video bg-black rounded overflow-hidden">
                        <img v-if="outputs.nightmare" :src="'data:image/jpeg;base64,' + outputs.nightmare"
                            class="w-full h-full object-contain" alt="Nightmare Output" />
                        <div v-else class="w-full h-full flex items-center justify-center text-gray-500">
                            No Output
                        </div>
                    </div>
                </div>

                <div class="bg-gray-800 rounded-lg p-6">
                    <h3 class="text-lg font-semibold mb-4 text-blue-400">🎨 Dream Output</h3>
                    <div class="aspect-video bg-black rounded overflow-hidden">
                        <img v-if="outputs.dream" :src="'data:image/jpeg;base64,' + outputs.dream"
                            class="w-full h-full object-contain" alt="Dream Output" />
                        <div v-else class="w-full h-full flex items-center justify-center text-gray-500">
                            No Output
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { io } from 'socket.io-client';

// Backend URL (can be configured)
const BACKEND_URL = 'http://localhost:5000';

// State
const connected = ref(false);
const status = ref(null);
const cameras = ref([
    { index: 0, name: 'Camera 0' },
    { index: 1, name: 'Camera 1' },
    { index: 2, name: 'Camera 2' }
]);
const selectedCameras = ref({
    nightmare: 0,  // Default: first camera
    dream: 1       // Default: second camera
});
const frames = ref({
    nightmare: null,
    dream: null
});
const outputs = ref({
    nightmare: null,
    dream: null
});
const recognition = ref({
    nightmare: '',
    dream: ''
});

let socket = null;

// Connect to backend
function connect() {
    socket = io(BACKEND_URL, {
        transports: ['websocket', 'polling']
    });

    socket.on('connect', () => {
        connected.value = true;
        console.log('[Config] Connected to backend');
    });

    socket.on('disconnect', () => {
        connected.value = false;
        console.log('[Config] Disconnected from backend');
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
        }
    });
}

// Update camera selection
function updateCamera(role) {
    const camIndex = selectedCameras.value[role];
    console.log(`[Config] Setting ${role} camera to ${camIndex}`);

    // Send to backend
    if (socket) {
        socket.emit('set_camera', { role, camera_index: camIndex });
    }
}

// Fetch available cameras from backend
async function fetchCameras() {
    try {
        const res = await fetch(`${BACKEND_URL}/cameras`);
        if (res.ok) {
            cameras.value = await res.json();
            console.log('[Config] Cameras loaded:', cameras.value);
        }
    } catch (e) {
        console.error('[Config] Failed to fetch cameras:', e);
    }
}

onMounted(async () => {
    connect();
    await fetchCameras();

    // Apply default camera selections after connection
    setTimeout(() => {
        updateCamera('nightmare');
        updateCamera('dream');
    }, 1000);
});

onUnmounted(() => {
    if (socket) {
        socket.disconnect();
    }
});
</script>
