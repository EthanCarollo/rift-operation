<template>
    <div class="relative w-full h-full bg-black overflow-hidden rounded-lg border-2 border-white/30 shadow-2xl">
        <!-- Local Video Feed (Mirrored) -->
        <video ref="videoRef" autoplay playsinline muted 
            class="absolute inset-0 w-full h-full object-cover transform scale-x-[-1] z-0"></video>
        
        <!-- Status / Error Overlay -->
        <div v-if="error" class="absolute inset-0 flex items-center justify-center bg-black/80 z-20 text-red-500 text-center p-2 text-xs font-mono">
            {{ error }}
        </div>
        <div v-else-if="!stream" class="absolute inset-0 flex items-center justify-center bg-black/80 z-20 text-neutral-500 text-xs animate-pulse">
            Connecting Camera...
        </div>

        <!-- AI Output Overlay -->
        <img v-if="outputFrame" :src="'data:image/png;base64,' + outputFrame"
            class="absolute inset-0 w-full h-full object-contain z-10 pointer-events-none" 
            alt="AI Output" />

        <!-- Label -->
        <div class="absolute bottom-0 left-0 right-0 bg-black/70 text-white text-[10px] px-1 py-0.5 text-center uppercase tracking-wider z-20">
            {{ role }}
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { io } from 'socket.io-client';

const props = defineProps({
    role: { type: String, required: true }, // 'dream' or 'nightmare'
    backendUrl: { type: String, required: true }
});

const videoRef = ref(null);
const stream = ref(null);
const error = ref(null);
const outputFrame = ref(null);
let socket = null;
let captureInterval = null;

// Config (could be props too)
const CAPTURE_RATE_MS = 200; // 5 FPS for AI processing
const JPEG_QUALITY = 0.85;

async function startCamera(overrideDeviceId = null) {
    try {
        error.value = null;
        
        let deviceId = overrideDeviceId;

        // Fallback to local config if no override
        if (!deviceId) {
            const savedConfig = localStorage.getItem('battle_camera_config');
            if (savedConfig) {
                const config = JSON.parse(savedConfig);
                deviceId = config[props.role];
            }
        }

        const constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        };

        if (deviceId) {
            constraints.video.deviceId = { exact: deviceId };
        }

        // Stop existing stream
        if (stream.value) {
            stream.value.getTracks().forEach(t => t.stop());
        }

        // 2. Start Stream
        stream.value = await navigator.mediaDevices.getUserMedia(constraints);
        if (videoRef.value) {
            videoRef.value.srcObject = stream.value;
        }

        startCaptureLoop();
        
        // Report success?

    } catch (e) {
        console.error(`[FrontCam] Error starting ${props.role} camera:`, e);
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
