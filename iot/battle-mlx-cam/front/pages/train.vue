<template>
    <div class="min-h-screen bg-neutral-900 text-neutral-200 p-4 font-mono text-sm">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4 border-b border-neutral-700 pb-3">
            <h1 class="text-lg font-bold">🧠 KNN Training</h1>
            <NuxtLink to="/config" class="px-3 py-1 border border-neutral-600 rounded hover:bg-neutral-800">
                ← Config
            </NuxtLink>
        </div>

        <!-- Layout -->
        <div class="grid grid-cols-2 gap-6">
            <!-- LEFT: Camera + Capture -->
            <div class="space-y-4">
                <h2 class="font-bold text-green-500">📷 Capture Training Data</h2>
                
                <!-- Camera Preview -->
                <div class="relative aspect-video bg-black rounded border border-neutral-700 overflow-hidden">
                    <video ref="videoRef" autoplay playsinline muted 
                        class="absolute inset-0 w-full h-full object-cover transform scale-x-[-1]"></video>
                        
                    <!-- Loading State -->
                    <div v-if="!stream && !cameraError" class="absolute inset-0 flex items-center justify-center text-neutral-500 animate-pulse">
                        Waiting for camera permission...
                    </div>
                    
                    <!-- Error State -->
                    <div v-if="cameraError" class="absolute inset-0 flex flex-col items-center justify-center text-red-400 p-4 text-center">
                        <span class="text-2xl mb-2">🚫</span>
                        <div class="font-bold">Camera Access Denied</div>
                        <div class="text-xs text-neutral-500 mb-4">{{ cameraError }}</div>
                        <button @click="startCamera" class="px-3 py-1 bg-neutral-800 hover:bg-neutral-700 rounded border border-neutral-600 text-xs text-white">
                            Retry Access
                        </button>
                    </div>
                </div>

                <!-- Label Input + Capture Button -->
                <div class="flex gap-2">
                    <input v-model="currentLabel" type="text" placeholder="Label (e.g. 'key', 'star')"
                        class="flex-1 bg-neutral-800 border border-neutral-700 rounded px-3 py-2 text-white" />
                    <button @click="captureSample" :disabled="!stream || !currentLabel"
                        class="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 rounded font-bold">
                        📸 Capture
                    </button>
                </div>

                <!-- Quick Labels -->
                <div class="flex flex-wrap gap-2">
                    <button v-for="label in quickLabels" :key="label" @click="currentLabel = label"
                        class="px-3 py-1 border rounded text-xs"
                        :class="currentLabel === label ? 'bg-green-600 border-green-500' : 'border-neutral-600 hover:bg-neutral-800'">
                        {{ label }}
                    </button>
                </div>

                <!-- Last Capture Feedback -->
                <div v-if="lastCapture" class="p-3 bg-neutral-800 rounded border border-neutral-700">
                    <span class="text-green-400">✅ Added:</span> {{ lastCapture }}
                </div>
            </div>

            <!-- RIGHT: Model Stats + Test -->
            <div class="space-y-4">
                <h2 class="font-bold text-blue-500">📊 Training Data</h2>

                <!-- Sample Counts -->
                <div class="p-4 bg-neutral-800 rounded border border-neutral-700">
                    <div v-if="Object.keys(samples).length === 0" class="text-neutral-500">
                        No samples yet. Capture some training data!
                    </div>
                    <div v-else class="space-y-2">
                        <div v-for="(count, label) in samples" :key="label" 
                            class="flex justify-between items-center text-sm">
                            <span>{{ label }}</span>
                            <div class="flex items-center gap-2">
                                <span class="text-neutral-400">{{ count }} samples</span>
                                <button @click="deleteLabel(label)" class="text-red-500 hover:text-red-400">🗑️</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Test Prediction -->
                <h2 class="font-bold text-purple-500 mt-6">🔮 Test Prediction</h2>
                <button @click="testPredict" :disabled="!stream"
                    class="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded font-bold">
                    Test Current Frame
                </button>

                <div v-if="prediction" class="p-4 bg-neutral-800 rounded border border-neutral-700">
                    <div class="text-2xl font-bold" :class="prediction.label === 'Unknown' ? 'text-red-400' : 'text-green-400'">
                        {{ prediction.label }}
                    </div>
                    <div class="text-neutral-400 text-xs">Distance: {{ prediction.distance.toFixed(2) }}</div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const config = useRuntimeConfig();
const backendUrl = ref(config.public.backendUrl);

const videoRef = ref(null);
const stream = ref(null);
const currentLabel = ref('');
const lastCapture = ref(null);
const samples = ref({});
const prediction = ref(null);

const quickLabels = ['key', 'door', 'star', 'eye', 'cloud', 'sword', 'empty', 'bullshit'];

const cameraError = ref(null);

async function startCamera() {
    cameraError.value = null;
    try {
        stream.value = await navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 640 }, height: { ideal: 480 } }
        });
        if (videoRef.value) {
            videoRef.value.srcObject = stream.value;
        }
    } catch (e) {
        console.error('[Train] Camera error:', e);
        cameraError.value = e.message || 'Unknown error';
    }
}

async function fetchSamples() {
    try {
        const res = await fetch(`${backendUrl.value}/knn/samples`);
        if (res.ok) {
            samples.value = await res.json();
        }
    } catch (e) {
        console.error('[Train] Failed to fetch samples:', e);
    }
}

async function captureSample() {
    if (!videoRef.value || !currentLabel.value) return;

    const canvas = document.createElement('canvas');
    canvas.width = videoRef.value.videoWidth;
    canvas.height = videoRef.value.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoRef.value, 0, 0);

    const imageB64 = canvas.toDataURL('image/jpeg', 0.85).split(',')[1];

    try {
        const res = await fetch(`${backendUrl.value}/knn/add_sample`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ label: currentLabel.value, image: imageB64 })
        });

        if (res.ok) {
            lastCapture.value = currentLabel.value;
            await fetchSamples();
        }
    } catch (e) {
        console.error('[Train] Failed to add sample:', e);
    }
}

async function testPredict() {
    if (!videoRef.value) return;

    const canvas = document.createElement('canvas');
    canvas.width = videoRef.value.videoWidth;
    canvas.height = videoRef.value.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoRef.value, 0, 0);

    const imageB64 = canvas.toDataURL('image/jpeg', 0.85).split(',')[1];

    try {
        const res = await fetch(`${backendUrl.value}/knn/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageB64 })
        });

        if (res.ok) {
            prediction.value = await res.json();
        }
    } catch (e) {
        console.error('[Train] Prediction error:', e);
    }
}

async function deleteLabel(label) {
    if (!confirm(`Delete all samples of "${label}"?`)) return;

    try {
        await fetch(`${backendUrl.value}/knn/delete_label`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ label })
        });
        await fetchSamples();
    } catch (e) {
        console.error('[Train] Failed to delete:', e);
    }
}

onMounted(() => {
    startCamera();
    fetchSamples();
});

onUnmounted(() => {
    if (stream.value) {
        stream.value.getTracks().forEach(t => t.stop());
    }
});
</script>
