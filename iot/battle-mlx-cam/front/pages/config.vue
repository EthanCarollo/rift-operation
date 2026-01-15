<template>
    <div class="min-h-screen bg-neutral-900 text-neutral-200 p-4 font-mono text-sm">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4 border-b border-neutral-700 pb-3">
            <h1 class="text-lg font-bold">Battle Camera Setup (Client-Side)</h1>
            <div class="flex items-center gap-4">
                <button @click="refreshDevices" class="px-3 py-1 bg-neutral-800 rounded hover:bg-neutral-700 text-xs">
                    🔄 Refresh Devices
                </button>
                <NuxtLink to="/" class="px-3 py-1 border border-neutral-600 rounded hover:bg-neutral-800">
                    ← Battle
                </NuxtLink>
            </div>
        </div>

        <div class="grid grid-cols-2 gap-8">
            <!-- Nightmare Config -->
            <div class="space-y-4">
                <h2 class="font-bold text-red-500 text-lg border-b border-red-900/30 pb-2">NIGHTMARE CAM</h2>
                
                <select v-model="config.nightmare" @change="saveConfig"
                    class="w-full bg-neutral-800 border border-neutral-700 rounded p-2">
                    <option value="">-- Select Camera --</option>
                    <option v-for="device in videoDevices" :key="device.deviceId" :value="device.deviceId">
                        {{ device.label || 'Unknown Camera' }}
                    </option>
                </select>

                <!-- Live Preview -->
                <div class="relative aspect-video bg-black rounded border border-neutral-800 overflow-hidden">
                     <video ref="nightmareVideo" autoplay playsinline muted 
                        class="w-full h-full object-cover transform scale-x-[-1]"></video>
                     <div class="absolute top-2 left-2 bg-black/50 px-2 py-1 rounded text-xs">Local Preview</div>
                </div>
            </div>

            <!-- Dream Config -->
            <div class="space-y-4">
                <h2 class="font-bold text-blue-500 text-lg border-b border-blue-900/30 pb-2">DREAM CAM</h2>
                
                <select v-model="config.dream" @change="saveConfig"
                    class="w-full bg-neutral-800 border border-neutral-700 rounded p-2">
                    <option value="">-- Select Camera --</option>
                    <option v-for="device in videoDevices" :key="device.deviceId" :value="device.deviceId">
                        {{ device.label || 'Unknown Camera' }}
                    </option>
                </select>

                <!-- Live Preview -->
                <div class="relative aspect-video bg-black rounded border border-neutral-800 overflow-hidden">
                     <video ref="dreamVideo" autoplay playsinline muted 
                        class="w-full h-full object-cover transform scale-x-[-1]"></video>
                     <div class="absolute top-2 left-2 bg-black/50 px-2 py-1 rounded text-xs">Local Preview</div>
                </div>
            </div>
        </div>

        <div class="mt-8 p-4 bg-neutral-800/50 rounded text-center text-neutral-500 text-xs">
            <p>Selection is saved to Browser LocalStorage automatically.</p>
            <p>Ensure you open this page on the <b>TARGET MACHINE</b> to configure its specific cameras.</p>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';

const videoDevices = ref([]);
const config = ref({
    nightmare: '',
    dream: ''
});

const nightmareVideo = ref(null);
const dreamVideo = ref(null);
const streams = { nightmare: null, dream: null };

async function refreshDevices() {
    try {
        // Request permission first to get labels
        await navigator.mediaDevices.getUserMedia({ video: true });
        
        const devices = await navigator.mediaDevices.enumerateDevices();
        videoDevices.value = devices.filter(d => d.kind === 'videoinput');
        
        console.log('Video Devices:', videoDevices.value);
    } catch (e) {
        console.error('Error fetching devices:', e);
        alert('Camera permission denied or error. Check console.');
    }
}

function saveConfig() {
    localStorage.setItem('battle_camera_config', JSON.stringify(config.value));
    updatePreviews();
}

async function startStream(deviceId, videoElement, role) {
    // Stop existing
    if (streams[role]) {
        streams[role].getTracks().forEach(t => t.stop());
        streams[role] = null;
    }

    if (!deviceId || !videoElement) return;

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { deviceId: { exact: deviceId } }
        });
        streams[role] = stream;
        videoElement.srcObject = stream;
    } catch (e) {
        console.error(`Failed to start ${role} stream:`, e);
    }
}

function updatePreviews() {
    startStream(config.value.nightmare, nightmareVideo.value, 'nightmare');
    startStream(config.value.dream, dreamVideo.value, 'dream');
}

onMounted(async () => {
    // Load config
    const saved = localStorage.getItem('battle_camera_config');
    if (saved) {
        try { config.value = JSON.parse(saved); } catch {}
    }

    await refreshDevices();
    updatePreviews();
});
</script>
