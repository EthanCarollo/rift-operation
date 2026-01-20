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

                <!-- Camera Selection -->
                <div class="flex gap-2">
                    <select v-model="selectedDeviceId" @change="switchCamera"
                        class="flex-1 bg-neutral-800 border border-neutral-700 rounded px-3 py-2 text-white text-sm">
                        <option :value="null">-- Select Camera --</option>
                        <option v-for="device in videoDevices" :key="device.deviceId" :value="device.deviceId">
                            {{ device.label || `Camera ${videoDevices.indexOf(device) + 1}` }}
                        </option>
                    </select>
                    <button @click="refreshDevices"
                        class="px-3 py-2 bg-neutral-700 hover:bg-neutral-600 rounded border border-neutral-600 text-xs">
                        🔄
                    </button>
                </div>

                <!-- Crop & Rotation Controls -->
                <div class="bg-neutral-800 p-3 rounded space-y-3">
                    <!-- Crop Toggle -->
                    <div class="flex items-center justify-between">
                        <label class="flex items-center gap-2 cursor-pointer">
                            <input type="checkbox" v-model="cropEnabled"
                                class="w-4 h-4 rounded bg-neutral-900 border-neutral-600 text-green-500">
                            <span class="text-xs text-neutral-300">✂️ Apply Crop</span>
                        </label>
                        <span v-if="cropEnabled && crop" class="text-xs text-neutral-500">
                            {{ Math.round(crop.w * 100) }}% x {{ Math.round(crop.h * 100) }}%
                        </span>
                    </div>

                    <!-- Crop Inputs (show if enabled) -->
                    <div v-if="cropEnabled" class="grid grid-cols-4 gap-2">
                        <div>
                            <label class="text-[10px] text-neutral-500">X</label>
                            <input type="number" v-model.number="crop.x" min="0" max="1" step="0.01"
                                class="w-full bg-neutral-900 border border-neutral-700 rounded px-2 py-1 text-xs text-white">
                        </div>
                        <div>
                            <label class="text-[10px] text-neutral-500">Y</label>
                            <input type="number" v-model.number="crop.y" min="0" max="1" step="0.01"
                                class="w-full bg-neutral-900 border border-neutral-700 rounded px-2 py-1 text-xs text-white">
                        </div>
                        <div>
                            <label class="text-[10px] text-neutral-500">Width</label>
                            <input type="number" v-model.number="crop.w" min="0" max="1" step="0.01"
                                class="w-full bg-neutral-900 border border-neutral-700 rounded px-2 py-1 text-xs text-white">
                        </div>
                        <div>
                            <label class="text-[10px] text-neutral-500">Height</label>
                            <input type="number" v-model.number="crop.h" min="0" max="1" step="0.01"
                                class="w-full bg-neutral-900 border border-neutral-700 rounded px-2 py-1 text-xs text-white">
                        </div>
                    </div>

                    <!-- Rotation -->
                    <div class="flex items-center gap-2">
                        <label class="text-xs text-neutral-400">🔄 Rotation:</label>
                        <div class="flex gap-1">
                            <button v-for="angle in [0, 90, 180, 270]" :key="angle" @click="rotation = angle"
                                class="px-2 py-1 text-xs rounded"
                                :class="rotation === angle ? 'bg-green-600 text-white' : 'bg-neutral-700 hover:bg-neutral-600'">
                                {{ angle }}°
                            </button>
                        </div>
                    </div>

                    <!-- Grayscale -->
                    <div class="flex items-center gap-2">
                        <label class="flex items-center gap-2 cursor-pointer">
                            <input type="checkbox" v-model="grayscale"
                                class="w-4 h-4 rounded bg-neutral-900 border-neutral-600 text-green-500">
                            <span class="text-xs text-neutral-300">⚫ Black & White</span>
                        </label>
                    </div>
                </div>

                <!-- Camera Preview -->
                <div class="relative aspect-video bg-black rounded border border-neutral-700 overflow-hidden">
                    <video ref="videoRef" autoplay playsinline muted
                        class="absolute inset-0 w-full h-full object-cover transform scale-x-[-1]"></video>

                    <!-- Crop Overlay Preview -->
                    <div v-if="cropEnabled && crop" class="absolute border-2 border-green-500 pointer-events-none"
                        :style="{
                            left: (crop.x * 100) + '%',
                            top: (crop.y * 100) + '%',
                            width: (crop.w * 100) + '%',
                            height: (crop.h * 100) + '%'
                        }"></div>

                    <!-- Loading State -->
                    <div v-if="!stream && !cameraError"
                        class="absolute inset-0 flex items-center justify-center text-neutral-500 animate-pulse">
                        {{ selectedDeviceId ? 'Starting camera...' : 'Select a camera above' }}
                    </div>

                    <!-- Error State -->
                    <div v-if="cameraError"
                        class="absolute inset-0 flex flex-col items-center justify-center text-red-400 p-4 text-center">
                        <span class="text-2xl mb-2">🚫</span>
                        <div class="font-bold">Camera Access Denied</div>
                        <div class="text-xs text-neutral-500 mb-4">{{ cameraError }}</div>
                        <button @click="switchCamera"
                            class="px-3 py-1 bg-neutral-800 hover:bg-neutral-700 rounded border border-neutral-600 text-xs text-white">
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
                    <div class="text-2xl font-bold"
                        :class="prediction.label === 'Unknown' ? 'text-red-400' : 'text-green-400'">
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

// Camera device selection
const videoDevices = ref([]);
const selectedDeviceId = ref(null);

// Crop & Rotation settings for training
const cropEnabled = ref(false);
const crop = ref({ x: 0.1, y: 0.1, w: 0.8, h: 0.8 });
const rotation = ref(0);
const grayscale = ref(false);

const quickLabels = ['sword', 'umbrella', 'sun', 'empty', 'bullshit'];

const cameraError = ref(null);

async function refreshDevices() {
    try {
        // Request permission first (needed to get device labels)
        const tempStream = await navigator.mediaDevices.getUserMedia({ video: true });
        tempStream.getTracks().forEach(t => t.stop());

        const devices = await navigator.mediaDevices.enumerateDevices();
        videoDevices.value = devices.filter(d => d.kind === 'videoinput');
        console.log('[Train] Found cameras:', videoDevices.value.length);

        // Auto-select first camera if none selected
        if (!selectedDeviceId.value && videoDevices.value.length > 0) {
            selectedDeviceId.value = videoDevices.value[0].deviceId;
            await switchCamera();
        }
    } catch (e) {
        console.error('[Train] Failed to enumerate devices:', e);
        cameraError.value = e.message || 'Failed to access cameras';
    }
}

async function switchCamera() {
    // Stop existing stream
    if (stream.value) {
        stream.value.getTracks().forEach(t => t.stop());
        stream.value = null;
    }

    if (!selectedDeviceId.value) return;

    cameraError.value = null;
    try {
        stream.value = await navigator.mediaDevices.getUserMedia({
            video: {
                deviceId: { exact: selectedDeviceId.value },
                width: { ideal: 640 },
                height: { ideal: 480 }
            }
        });
        if (videoRef.value) {
            videoRef.value.srcObject = stream.value;
        }
        console.log('[Train] Switched to camera:', selectedDeviceId.value);
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

    const videoWidth = videoRef.value.videoWidth;
    const videoHeight = videoRef.value.videoHeight;

    // Create a canvas for the full frame first
    let canvas = document.createElement('canvas');
    canvas.width = videoWidth;
    canvas.height = videoHeight;
    let ctx = canvas.getContext('2d');
    ctx.drawImage(videoRef.value, 0, 0);

    // Apply crop if enabled
    if (cropEnabled.value && crop.value) {
        const left = Math.round(crop.value.x * videoWidth);
        const top = Math.round(crop.value.y * videoHeight);
        const width = Math.round(crop.value.w * videoWidth);
        const height = Math.round(crop.value.h * videoHeight);

        if (width > 0 && height > 0) {
            const croppedCanvas = document.createElement('canvas');
            croppedCanvas.width = width;
            croppedCanvas.height = height;
            const croppedCtx = croppedCanvas.getContext('2d');
            croppedCtx.drawImage(canvas, left, top, width, height, 0, 0, width, height);
            canvas = croppedCanvas;
            ctx = croppedCtx;
        }
    }

    // Apply rotation if set
    if (rotation.value !== 0) {
        const rotatedCanvas = document.createElement('canvas');
        const rotatedCtx = rotatedCanvas.getContext('2d');

        if (rotation.value === 90 || rotation.value === 270) {
            rotatedCanvas.width = canvas.height;
            rotatedCanvas.height = canvas.width;
        } else {
            rotatedCanvas.width = canvas.width;
            rotatedCanvas.height = canvas.height;
        }

        rotatedCtx.translate(rotatedCanvas.width / 2, rotatedCanvas.height / 2);
        rotatedCtx.rotate((rotation.value * Math.PI) / 180);
        rotatedCtx.drawImage(canvas, -canvas.width / 2, -canvas.height / 2);
        canvas = rotatedCanvas;
    }

    // Apply grayscale if set
    if (grayscale.value) {
        const grayCanvas = document.createElement('canvas');
        grayCanvas.width = canvas.width;
        grayCanvas.height = canvas.height;
        const grayCtx = grayCanvas.getContext('2d');
        grayCtx.drawImage(canvas, 0, 0);
        const imageData = grayCtx.getImageData(0, 0, grayCanvas.width, grayCanvas.height);
        const data = imageData.data;
        for (let i = 0; i < data.length; i += 4) {
            const avg = (data[i] + data[i + 1] + data[i + 2]) / 3;
            data[i] = avg;
            data[i + 1] = avg;
            data[i + 2] = avg;
        }
        grayCtx.putImageData(imageData, 0, 0);
        canvas = grayCanvas;
    }

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

    const videoWidth = videoRef.value.videoWidth;
    const videoHeight = videoRef.value.videoHeight;

    let canvas = document.createElement('canvas');
    canvas.width = videoWidth;
    canvas.height = videoHeight;
    let ctx = canvas.getContext('2d');
    ctx.drawImage(videoRef.value, 0, 0);

    // Apply crop if enabled
    if (cropEnabled.value && crop.value) {
        const left = Math.round(crop.value.x * videoWidth);
        const top = Math.round(crop.value.y * videoHeight);
        const width = Math.round(crop.value.w * videoWidth);
        const height = Math.round(crop.value.h * videoHeight);

        if (width > 0 && height > 0) {
            const croppedCanvas = document.createElement('canvas');
            croppedCanvas.width = width;
            croppedCanvas.height = height;
            const croppedCtx = croppedCanvas.getContext('2d');
            croppedCtx.drawImage(canvas, left, top, width, height, 0, 0, width, height);
            canvas = croppedCanvas;
        }
    }

    // Apply rotation if set
    if (rotation.value !== 0) {
        const rotatedCanvas = document.createElement('canvas');
        const rotatedCtx = rotatedCanvas.getContext('2d');

        if (rotation.value === 90 || rotation.value === 270) {
            rotatedCanvas.width = canvas.height;
            rotatedCanvas.height = canvas.width;
        } else {
            rotatedCanvas.width = canvas.width;
            rotatedCanvas.height = canvas.height;
        }

        rotatedCtx.translate(rotatedCanvas.width / 2, rotatedCanvas.height / 2);
        rotatedCtx.rotate((rotation.value * Math.PI) / 180);
        rotatedCtx.drawImage(canvas, -canvas.width / 2, -canvas.height / 2);
        canvas = rotatedCanvas;
    }

    // Apply grayscale if set
    if (grayscale.value) {
        const grayCanvas = document.createElement('canvas');
        grayCanvas.width = canvas.width;
        grayCanvas.height = canvas.height;
        const grayCtx = grayCanvas.getContext('2d');
        grayCtx.drawImage(canvas, 0, 0);
        const imageData = grayCtx.getImageData(0, 0, grayCanvas.width, grayCanvas.height);
        const data = imageData.data;
        for (let i = 0; i < data.length; i += 4) {
            const avg = (data[i] + data[i + 1] + data[i + 2]) / 3;
            data[i] = avg;
            data[i + 1] = avg;
            data[i + 2] = avg;
        }
        grayCtx.putImageData(imageData, 0, 0);
        canvas = grayCanvas;
    }

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
    refreshDevices();
    fetchSamples();
});

onUnmounted(() => {
    if (stream.value) {
        stream.value.getTracks().forEach(t => t.stop());
    }
});
</script>
