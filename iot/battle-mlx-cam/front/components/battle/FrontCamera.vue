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

async function startCamera() {
    try {
        error.value = null;
        // 1. Get Config
        const savedConfig = localStorage.getItem('battle_camera_config');
        let deviceId = null;
        if (savedConfig) {
            const config = JSON.parse(savedConfig);
            deviceId = config[props.role];
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

        // 2. Start Stream
        stream.value = await navigator.mediaDevices.getUserMedia(constraints);
        if (videoRef.value) {
            videoRef.value.srcObject = stream.value;
        }

        startCaptureLoop();

    } catch (e) {
        console.error(`[FrontCam] Error starting ${props.role} camera:`, e);
        error.value = `Camera Error: ${e.message}`;
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
            
            // Mirror if needed (to match display) - actually backend expects original usually?
            // Let's send original, AI transforms usually handle flipping if needed or we flip only display.
            ctx.drawImage(videoRef.value, 0, 0);

            // Compress
            // remove data:image/jpeg;base64, prefix for backend? Depends on backend.
            // Current backend expects raw base64 bytes usually? No, let's verify backend expected format.
            // Backend web_server.py usually broadcasts.
            // We need a NEW event 'process_frame' on backend.
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
    });

    // Receive processed result
    socket.on('output_frame', (data) => {
        if (data.role === props.role && data.frame) {
            outputFrame.value = data.frame;
        }
    });

    // Also listen for recognition status or other signals if needed
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
