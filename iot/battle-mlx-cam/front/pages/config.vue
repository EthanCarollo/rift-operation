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

                <!-- AI Output Preview (from Backend) -->
                <div class="relative aspect-video bg-black rounded border border-neutral-800 overflow-hidden group">
                     <img v-if="outputs.nightmare" :src="'data:image/png;base64,' + outputs.nightmare"
                        class="absolute inset-0 w-full h-full object-contain" />
                     <div v-else class="absolute inset-0 flex items-center justify-center text-neutral-600">
                        Waiting for AI Output...
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

                <!-- AI Output Preview (from Backend) -->
                <div class="relative aspect-video bg-black rounded border border-neutral-800 overflow-hidden group">
                     <img v-if="outputs.dream" :src="'data:image/png;base64,' + outputs.dream"
                        class="absolute inset-0 w-full h-full object-contain" />
                     <div v-else class="absolute inset-0 flex items-center justify-center text-neutral-600">
                        Waiting for AI Output...
                     </div>
                     <div class="absolute top-2 left-2 bg-black/50 px-2 py-1 rounded text-xs">AI Output</div>
                </div>
            </div>
        </div>

        <div class="mt-8 p-4 bg-neutral-800/50 rounded text-center text-neutral-500 text-xs">
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

let socket = null;

function connect() {
    socket = io(backendUrl.value, { transports: ['websocket', 'polling'] });

    socket.on('connect', () => {
        connected.value = true;
        console.log('[Config] Connected to Backend');
        
        // Request initial data
        fetchRemoteDevices();
        fetchAssignments();
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
            outputs.value[data.role] = data.frame;
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
            // Only update if we don't have local selection? or simple sync
            if (data.nightmare) assignments.value.nightmare = data.nightmare;
            if (data.dream) assignments.value.dream = data.dream;
        }
    } catch (e) {
        console.error('Failed to fetch assignments:', e);
    }
}

onMounted(() => {
    connect();
});

onUnmounted(() => {
    if (socket) socket.disconnect();
});
</script>
