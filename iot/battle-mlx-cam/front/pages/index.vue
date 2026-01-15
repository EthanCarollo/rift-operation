<template>
    <div class="fixed inset-0 bg-black flex flex-col overflow-hidden font-mono select-none cursor-none"
        @click="unlockAudio">

        <!-- Hidden Audio Controller (BattleHUD without visible UI) -->
        <BattleHUD ref="hudRef" 
            :is-connected="isConnected" 
            :show-debug="false" 
            :state="battleState"
            :hp="currentHp" 
            :attack="currentAttack" 
            :video-name="''"
            :current-music="currentMusic" 
            :should-loop="musicShouldLoop" 
            :is-vertical="false"
            class="hidden" />

        <!-- Main Battle Layout: Dynamic height based on camera visibility -->
        <div class="flex flex-col w-full h-full">
            
            <!-- TOP: Video/Boss Area -->
            <div class="relative w-full bg-black overflow-hidden" 
                 :class="showCamera ? 'h-[70%]' : 'h-full'">
                <!-- Video Layer with fade transition -->
                <video v-show="currentVideo && !videoError" ref="videoRef"
                    class="absolute inset-0 w-full h-full object-cover z-0 transition-opacity duration-500"
                    :class="videoReady ? 'opacity-100' : 'opacity-0'"
                    :src="currentVideo" autoplay loop muted playsinline preload="auto"
                    @error="handleVideoError" @loadeddata="onVideoReady" @canplay="onVideoReady" />

                <!-- IDLE BG / Loading State -->
                <div v-if="battleState === 'IDLE' || !currentVideo || !videoReady"
                    class="absolute inset-0 z-10 bg-black flex items-center justify-center transition-opacity duration-300"
                    :class="videoReady && battleState !== 'IDLE' ? 'opacity-0 pointer-events-none' : 'opacity-100'">
                    <div class="text-purple-500/30 text-xl animate-pulse">EN ATTENTE...</div>
                </div>

                <!-- Boss Overlay -->
                <BattleBoss v-if="battleState !== 'IDLE' && !isEndState" 
                    :is-hit="isHit" :attack="currentAttack" :is-vertical="false" />
            </div>

            <!-- BOTTOM: Camera Area (30%) - Only visible when not IDLE or debugMode -->
            <div v-if="showCamera" class="relative w-full h-[30%] bg-neutral-900 overflow-hidden">
                <BattleFrontCamera 
                    v-if="pureRole"
                    :role="pureRole"
                    :backend-url="config.public.backendUrl"
                    class="w-full h-full"
                />
                <div v-else class="absolute inset-0 flex items-center justify-center text-white/30 text-sm">
                    📷 Rôle non défini (ajouter ?role=dream ou ?role=nightmare)
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { io } from 'socket.io-client';
import BattleBoss from '~/components/battle/BattleBoss.vue';
import BattleHUD from '~/components/battle/BattleHUD.vue';
import { useBattleState } from '~/composables/useBattleState';

// --- CONFIG ---
const config = useRuntimeConfig();
const route = useRoute();

// Role from URL query param only (no selector screen)
const selectedRole = ref(route.query.role || null);

// Debug mode from backend (synced)
const debugMode = ref(false);
let socket = null;

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
} = useBattleState(false); // debug = false

// --- VIDEO TRANSITION ---
const videoReady = ref(false);
let lastVideoSrc = '';

function onVideoReady() {
    videoReady.value = true;
    onVideoLoaded();
}

// Watch for video source changes to reset ready state
watch(currentVideo, (newSrc) => {
    if (newSrc !== lastVideoSrc) {
        videoReady.value = false;
        lastVideoSrc = newSrc;
    }
});

// --- COMPUTED ---
const isEndState = computed(() => {
    return battleState.value === 'WEAKENED' || battleState.value === 'CAPTURED';
});

// Show camera only when NOT in IDLE (in battle mode)
const showCamera = computed(() => {
    return battleState.value !== 'IDLE';
});

// --- SOCKET CONNECTION FOR DEBUG MODE ---
function connectDebugSocket() {
    socket = io(config.public.backendUrl, { transports: ['websocket', 'polling'] });
    
    socket.on('connect', () => {
        console.log('[Battle] Connected to backend for debug sync');
        // Fetch initial debug mode
        fetchDebugMode();
    });
    
    socket.on('debug_mode_changed', (data) => {
        console.log('[Battle] Debug mode changed:', data.enabled);
        debugMode.value = data.enabled;
    });
}

async function fetchDebugMode() {
    try {
        const res = await fetch(`${config.public.backendUrl}/remote/debug_mode`);
        if (res.ok) {
            const data = await res.json();
            debugMode.value = data.debug_mode || false;
        }
    } catch (e) {
        console.error('[Battle] Failed to fetch debug mode:', e);
    }
}

// --- LIFECYCLE ---
onMounted(() => {
    connectDebugSocket();
    init();
});

onUnmounted(() => {
    if (socket) socket.disconnect();
});
</script>
