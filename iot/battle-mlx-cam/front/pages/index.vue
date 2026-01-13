<template>
    <div class="fixed inset-0 bg-black flex flex-col overflow-hidden font-mono select-none"
        :class="{ 'cursor-none': selectedRole }" @click="unlockAudio">

        <!-- 1. ROLL SELECTION SCREEN (Initial State) -->
        <div v-if="!selectedRole" class="absolute inset-0 z-50 flex flex-col items-center justify-center bg-[#0a0a0a]">
            <div class="grid place-items-center gap-12">
                <div
                    class="relative w-32 h-32 border-4 border-purple-500/30 rounded-full animate-pulse flex items-center justify-center">
                    <div class="w-24 h-24 border-2 border-purple-500/60 rounded-full" />
                    <div
                        class="absolute w-full h-[2px] bg-purple-500 animate-[scan_2s_ease-in-out_infinite] opacity-50" />
                </div>
                <div class="text-center space-y-3">
                    <h1 class="text-4xl font-black tracking-[0.2em] text-purple-400 glitch-text">
                        BATAILLE FINALE
                    </h1>
                    <p class="text-sm tracking-widest opacity-70 uppercase text-purple-300 mb-8">
                        EN ATTENTE DES AGENTS
                    </p>

                    <!-- Role Buttons: VERTICAL MODE -->
                    <div class="flex gap-8 justify-center mb-6">
                        <button @click="selectedRole = 'dream'"
                            class="px-8 py-4 bg-pink-600 border-2 border-pink-400 hover:bg-pink-500 hover:scale-105 text-white font-black tracking-widest rounded transition-all duration-300 uppercase shadow-[0_0_30px_rgba(219,39,119,0.4)] text-xl">
                            DREAM
                        </button>
                        <button @click="selectedRole = 'nightmare'"
                            class="px-8 py-4 bg-blue-600 border-2 border-blue-400 hover:bg-blue-500 hover:scale-105 text-white font-black tracking-widest rounded transition-all duration-300 uppercase shadow-[0_0_30px_rgba(37,99,235,0.4)] text-xl">
                            NIGHTMARE
                        </button>
                    </div>

                    <!-- Role Buttons: DEV MODE -->
                    <div class="flex gap-4 justify-center opacity-70 scale-90">
                        <button @click="selectedRole = 'dream-dev'"
                            class="px-4 py-2 bg-pink-900/40 border border-pink-500/50 hover:bg-pink-600/40 text-pink-300 text-xs font-bold tracking-widest rounded transition-all uppercase">
                            DREAM DEV
                        </button>
                        <button @click="selectedRole = 'nightmare-dev'"
                            class="px-4 py-2 bg-blue-900/40 border border-blue-500/50 hover:bg-blue-600/40 text-blue-300 text-xs font-bold tracking-widest rounded transition-all uppercase">
                            NIGHTMARE DEV
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 2. BATTLE VIEW (Role Selected) -->
        <template v-else>
            <!-- IDLE STATE (Minimal Black Screen + Status) -->
            <!-- Note: We keep this outside rigid rotation if strictly just black, 
            BUT status needs to be rotated too so user can read it. 
            So everything goes inside the rotation wrapper. -->

            <div id="battle-container" class="absolute inset-0 w-full h-full bg-black">

                <!-- Video Layer -->
                <video v-show="currentVideo && !videoError && battleState !== 'IDLE'" ref="videoRef"
                    class="absolute inset-0 w-full h-full object-cover z-0" :src="currentVideo" autoplay loop muted
                    playsinline @error="handleVideoError" @loadeddata="onVideoLoaded" />

                <!-- IDLE BG -->
                <div v-if="battleState === 'IDLE'"
                    class="absolute inset-0 z-10 bg-black flex items-center justify-center">
                </div>

                <!-- BATTLE UI OVERLAY -->
                <div class="absolute inset-0 z-10 pointer-events-none" :class="{ 'vertical-layout': isVertical }">
                    <BattleHUD ref="hudRef" :is-connected="isConnected" :show-debug="showDebug" :state="battleState"
                        :hp="currentHp" :attack="currentAttack" :video-name="currentVideo?.split('/').pop() || 'None'"
                        :current-music="currentMusic" :should-loop="musicShouldLoop" :is-vertical="isVertical"
                        @simulate="simulateRecon" @capture="simulateCapture" />

                    <template v-if="battleState !== 'IDLE'">
                        <BattleBoss v-if="!isEndState" :is-hit="isHit" :attack="currentAttack"
                            :is-vertical="isVertical" />
                        <BattleAgent v-if="!isEndState" :dream-valid="dreamCounterValid"
                            :nightmare-valid="nightmareCounterValid" :is-attacking="isAttacking"
                            :drawing-data="currentRoleDrawing" :is-vertical="isVertical" @attack="triggerAttack" />
                        <BattleState :message="stateMessage" :sub-message="stateSubMessage"
                            :message-class="stateMessageClass" :is-vertical="isVertical" />
                    </template>
                </div>

                <!-- CAMERA FEED OVERLAY (Bottom Left) -->
                <div v-if="battleState !== 'IDLE'" 
                     class="absolute bottom-4 left-4 z-30 w-48 aspect-video rounded-lg overflow-hidden border-2 border-white/30 shadow-2xl bg-black">
                    <!-- Live Camera Feed -->
                    <img v-if="cameraFrame" :src="'data:image/jpeg;base64,' + cameraFrame"
                        class="absolute inset-0 w-full h-full object-cover" alt="Camera" />
                    <div v-else class="absolute inset-0 flex items-center justify-center text-white/50 text-xs">
                        📷 No Feed
                    </div>
                    <!-- AI Drawing Overlay -->
                    <img v-if="outputFrame" :src="'data:image/png;base64,' + outputFrame"
                        class="absolute inset-0 w-full h-full object-contain z-10" alt="Drawing" />
                    <!-- Label -->
                    <div class="absolute bottom-0 left-0 right-0 bg-black/70 text-white text-[10px] px-1 py-0.5 text-center uppercase tracking-wider z-20">
                        {{ pureRole || 'Camera' }}
                    </div>
                </div>
            </div>
        </template>
    </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { io } from 'socket.io-client';
import BattleHUD from '~/components/battle/BattleHUD.vue';
import BattleBoss from '~/components/battle/BattleBoss.vue';
import BattleAgent from '~/components/battle/BattleAgent.vue';
import BattleState from '~/components/battle/BattleState.vue';
import { useBattleState } from '~/composables/useBattleState';

// definePageMeta({ layout: false }); // REMOVE FOR APP.VUE

// --- CONFIG ---
const config = useRuntimeConfig();
const showDebug = ref(true);
const route = useRoute();
const selectedRole = ref(route.query.role || null); // 'dream' | 'nightmare' | 'dream-dev' | 'nightmare-dev'

// --- CAMERA FEED STATE ---
const cameraFrame = ref(null);
const outputFrame = ref(null);
let backendSocket = null;

// Pure role name (without -dev suffix)
const pureRole = computed(() => {
    if (!selectedRole.value) return null;
    return selectedRole.value.replace('-dev', '');
});

// --- COMPOSABLE ---
const {
    battleState, currentHp, currentAttack, currentVideo, currentMusic, musicShouldLoop,
    dreamDrawingImage, nightmareDrawingImage, isAttacking, isHit, videoError, isConnected,
    dreamCounterValid, nightmareCounterValid, stateMessage, stateSubMessage, stateMessageClass,
    hudRef, videoRef,
    init, triggerAttack, simulateCapture, simulateRecon, unlockAudio, handleVideoError, onVideoLoaded
} = useBattleState(showDebug.value);

// --- BACKEND SOCKET FOR CAMERA ---
function connectBackend() {
    const backendUrl = config.public.backendUrl || 'http://localhost:5010';
    console.log('[Battle] Connecting to backend for camera:', backendUrl);
    
    backendSocket = io(backendUrl, { transports: ['websocket', 'polling'] });
    
    backendSocket.on('connect', () => {
        console.log('[Battle] Backend connected');
    });
    
    backendSocket.on('camera_frame', (data) => {
        if (data.role === pureRole.value && data.frame) {
            cameraFrame.value = data.frame;
        }
    });
    
    backendSocket.on('output_frame', (data) => {
        if (data.role === pureRole.value && data.frame) {
            outputFrame.value = data.frame;
        }
    });
}

// --- KEYBOARD SHORTCUTS ---
function handleKeydown(e) {
    // Only handle shortcuts when a role is selected (in battle view)
    if (!selectedRole.value) return;

    // Ignore if typing in an input
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    switch (e.key.toLowerCase()) {
        case 'r':
            e.preventDefault();
            simulateRecon();
            console.log('[Keyboard] R pressed → Simulate Recon');
            break;
        case 'c':
            e.preventDefault();
            simulateCapture();
            console.log('[Keyboard] C pressed → Simulate Capture');
            break;
        case ' ':
            e.preventDefault();
            triggerAttack();
            console.log('[Keyboard] Space pressed → Attack');
            break;
    }
}

// --- COMPUTED ---
// isVertical is false since screens are already in portrait orientation
const isVertical = computed(() => false);

// No rotation needed - screens are already vertical
const rotationStyle = computed(() => ({
    width: '100%',
    height: '100%'
}));

const isEndState = computed(() => {
    return battleState.value === 'WEAKENED' || battleState.value === 'CAPTURED';
});

const currentRoleDrawing = computed(() => {
    if (selectedRole.value === 'dream' || selectedRole.value === 'dream-dev') return dreamDrawingImage.value;
    if (selectedRole.value === 'nightmare' || selectedRole.value === 'nightmare-dev') return nightmareDrawingImage.value;
    return null;
});

// --- LIFECYCLE ---
onMounted(() => {
    init();
    connectBackend();
    window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
    if (backendSocket) backendSocket.disconnect();
});
</script>

<style scoped>
@keyframes scan {
    0% {
        top: 0%;
        opacity: 0;
    }

    50% {
        opacity: 1;
    }

    100% {
        top: 100%;
        opacity: 0;
    }
}

.glitch-text {
    text-shadow: 2px 0 #a855f7, -2px 0 #06b6d4;
    animation: glitch 3s infinite alternate-reverse;
}

@keyframes glitch {
    0% {
        transform: skewX(0deg);
        opacity: 1;
    }

    5% {
        transform: skewX(10deg);
        opacity: 0.8;
    }

    10% {
        transform: skewX(-10deg);
        opacity: 1;
    }

    15%,
    100% {
        transform: skewX(0deg);
        opacity: 1;
    }
}
</style>
