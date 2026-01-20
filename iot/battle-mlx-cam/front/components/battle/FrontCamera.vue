<template>
    <div class="relative w-full h-full overflow-hidden">
        <!-- Local Video Feed (Mirrored) -->
        <video ref="videoRef" autoplay playsinline muted
            class="absolute inset-0 w-full h-full object-cover z-0"></video>

        <!-- Status / Error Overlay -->
        <div v-if="error"
            class="absolute inset-0 flex items-center justify-center bg-black/80 z-20 text-red-500 text-center p-2 text-xs font-mono">
            {{ error }}
        </div>
        <div v-else-if="!stream"
            class="absolute inset-0 flex items-center justify-center bg-black/80 z-20 text-neutral-500 text-xs animate-pulse">
            Connecting Camera...
        </div>

        <!-- AI Output Overlay -->
        <img v-if="outputFrame && state !== 'IDLE'" :src="'data:image/png;base64,' + outputFrame"
            class="absolute inset-0 w-full h-full object-contain z-10 pointer-events-none" alt="AI Output" />

        <!-- Label -->
        <div
            class="absolute bottom-0 left-0 right-0 bg-black/70 text-white text-[10px] px-1 py-0.5 text-center uppercase tracking-wider z-20">
            {{ role }}
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { io } from 'socket.io-client';

const props = defineProps({
    role: { type: String, required: true }, // 'dream' or 'nightmare'
    backendUrl: { type: String, required: true },
    state: { type: String, default: 'IDLE' }
});

const videoRef = ref(null);
const stream = ref(null);
const error = ref(null);
const outputFrame = ref(null);
let socket = null;
let captureInterval = null;

// Config - Capture rate for AI processing
const CAPTURE_RATE_MS = 2000; // 2 seconds between frames
const JPEG_QUALITY = 0.85;

async function startCamera(overrideDeviceId = null, retryWithAny = false) {
    try {
        error.value = null;

        let deviceId = overrideDeviceId;

        // Fallback to local config if no override (skip if retrying with any)
        if (!deviceId && !retryWithAny) {
            const savedConfig = localStorage.getItem('battle_camera_config');
            if (savedConfig) {
                const config = JSON.parse(savedConfig);
                deviceId = config[props.role];
                if (deviceId) {
                    console.log(`[FrontCam:${props.role}] Using saved deviceId:`, deviceId);
                }
            }
        }

        const constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        };

        // Only use exact deviceId if we have one and not retrying with any
        if (deviceId && !retryWithAny) {
            constraints.video.deviceId = { exact: deviceId };
        }

        // Stop existing stream
        if (stream.value) {
            stream.value.getTracks().forEach(t => t.stop());
        }

        console.log(`[FrontCam:${props.role}] Requesting camera with constraints:`, constraints.video.deviceId ? 'specific device' : 'any device');

        // Start Stream
        stream.value = await navigator.mediaDevices.getUserMedia(constraints);
        if (videoRef.value) {
            videoRef.value.srcObject = stream.value;
        }

        console.log(`[FrontCam:${props.role}] Camera started successfully`);
        startCaptureLoop();

    } catch (e) {
        console.error(`[FrontCam:${props.role}] Error starting camera:`, e);

        // If device not found, retry with any available camera
        if (e.name === 'NotFoundError' || e.name === 'OverconstrainedError' || e.message.includes('not found')) {
            console.warn(`[FrontCam:${props.role}] Device not found, retrying with any camera...`);
            // Clear saved config for this role
            localStorage.removeItem('battle_camera_config');

            if (!retryWithAny) {
                return startCamera(null, true); // Retry without specific deviceId
            }
        }

        error.value = `Camera Error: ${e.message}`;
    }
}

async function registerDevices() {
    try {
        // Ensure perm first
        await navigator.mediaDevices.getUserMedia({ video: true });
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoInputs = devices
            .filter(d => d.kind === 'videoinput')
            .map(d => ({ deviceId: d.deviceId, label: d.label }));

        console.log('[FrontCam] Registering devices:', videoInputs);
        socket.emit('register_client', { devices: videoInputs });

    } catch (e) {
        console.error('[FrontCam] Failed to register devices:', e);
    }
}

function startCaptureLoop() {
    if (captureInterval) clearInterval(captureInterval);

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    captureInterval = setInterval(() => {
        if (!videoRef.value || !socket || !socket.connected) return;

        try {
            // Check if video is ready
            if (videoRef.value.readyState < 2) return;

            // Draw to canvas
            canvas.width = videoRef.value.videoWidth;
            canvas.height = videoRef.value.videoHeight;
            ctx.drawImage(videoRef.value, 0, 0);

            // Compress and send
            const dataUrl = canvas.toDataURL('image/jpeg', JPEG_QUALITY);
            const base64Data = dataUrl.split(',')[1];

            socket.emit('process_frame', {
                role: props.role,
                image: base64Data
            });

        } catch (e) {
            console.error('Capture frame error:', e);
        }
    }, CAPTURE_RATE_MS);
}

function connectSocket() {
    socket = io(props.backendUrl, { transports: ['websocket', 'polling'] });

    socket.on('connect', () => {
        console.log(`[FrontCam:${props.role}] Socket Connected`);
        // Register devices only once (e.g. from first role to connect? or both? doesn't matter)
        registerDevices();
    });

    // Receive processed result
    socket.on('output_frame', (data) => {
        if (data.role === props.role && data.frame) {
            outputFrame.value = data.frame;
        }
    });

    // Remote Configuration
    socket.on('set_device', (data) => {
        if (data.role === props.role && data.deviceId) {
            console.log(`[FrontCam] Remote config received for ${props.role}:`, data.deviceId);
            // Save to local storage for persistence
            const saved = localStorage.getItem('battle_camera_config') || '{}';
            const config = JSON.parse(saved);
            config[props.role] = data.deviceId;
            localStorage.setItem('battle_camera_config', JSON.stringify(config));

            // Apply
            startCamera(data.deviceId);
        }
    });
}

onMounted(() => {
    startCamera();
    connectSocket();
});

onUnmounted(() => {
    if (stream.value) {
        stream.value.getTracks().forEach(t => t.stop());
    }
    if (captureInterval) clearInterval(captureInterval);
    if (socket) socket.disconnect();
});
</script>
