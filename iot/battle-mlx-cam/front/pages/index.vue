<template>
    <div class="fixed inset-0 bg-black flex flex-col overflow-hidden font-mono select-none cursor-none"
        @click="unlockAudio">

        <!-- Hidden Audio Controller (BattleHUD without visible UI) -->
        <BattleHUD ref="hudRef" :is-connected="isConnected" :show-debug="false" :state="battleState" :hp="currentHp"
            :attack="currentAttack" :video-name="''" :current-music="currentMusic" :should-loop="musicShouldLoop"
            :is-vertical="false" class="hidden" />

        <!-- Main Battle Layout: Dynamic height based on camera visibility -->
        <div class="flex flex-col w-full h-full">

            <!-- TOP: Video/Boss Area -->
            <div class="relative w-full bg-black overflow-hidden" :class="showCamera ? 'h-[70%]' : 'h-full'">
                <!-- Video Layer with fade transition -->
                <video v-show="currentVideo && !videoError" ref="videoRef"
                    class="absolute inset-0 w-full h-full object-cover z-0 transition-opacity duration-500"
                    :class="videoReady ? 'opacity-100' : 'opacity-0'" :src="currentVideo" autoplay loop muted
                    playsinline preload="auto" @error="handleVideoError" @loadeddata="onVideoReady"
                    @canplay="onVideoReady" />

                <!-- IDLE BG / Loading State - Just black screen -->
                <div v-if="battleState === 'IDLE' || !currentVideo || !videoReady"
                    class="absolute inset-0 z-10 bg-black transition-opacity duration-300"
                    :class="videoReady && battleState !== 'IDLE' ? 'opacity-0 pointer-events-none' : 'opacity-100'">
                </div>

                <!-- Boss Overlay -->
                <BattleBoss v-if="battleState !== 'IDLE' && !isEndState" :is-hit="isHit" :attack="currentAttack"
                    :is-vertical="false" />

                <!-- Narrative Text Overlay - Lower position, below top area -->
                <div v-if="showNarrativeText"
                    class="absolute top-[15%] left-0 right-0 z-20 flex justify-center pointer-events-none">
                    <div class="bg-black/80 px-8 py-4 rounded-lg max-w-2xl text-center">
                        <p class="text-white text-lg md:text-xl font-medium leading-relaxed animate-fade-in">
                            {{ narrativeText }}
                        </p>
                    </div>
                </div>

                <!-- Drawing Validation Feedback + Loading Bar -->
                <div v-if="showDrawingFeedback || isGenerating"
                    class="absolute bottom-[35%] left-1/2 transform -translate-x-1/2 z-30 transition-all duration-300">
                    
                    <!-- Validation Badge -->
                    <div v-if="showDrawingFeedback && !isGenerating" class="px-6 py-3 rounded-full text-lg font-bold animate-bounce"
                        :class="isDrawingValid ? 'bg-green-500 text-white' : 'bg-red-500/80 text-white'">
                        {{ isDrawingValid ? '✓ Dessin validé !' : '✗ Essayez autre chose...' }}
                    </div>
                    
                    <!-- Loading Bar for AI Generation -->
                    <div v-if="isGenerating" class="flex flex-col items-center gap-3">
                        <div class="text-white text-lg font-medium animate-pulse">🎨 Génération en cours...</div>
                        <div class="w-64 h-2 bg-neutral-700 rounded-full overflow-hidden">
                            <div class="h-full bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500 rounded-full animate-loading-bar"></div>
                        </div>
                    </div>
                </div>

                <!-- Flying Generated Image Animation -->
                <div v-if="flyingImage" ref="flyingImageRef"
                    class="absolute z-40 fly-to-enemy pointer-events-none"
                    :style="flyingImageStyle">
                    <img :src="flyingImage" class="w-40 h-40 object-contain drop-shadow-2xl" />
                </div>

                <!-- Victory Typewriter Message -->
                <div v-if="showVictoryMessage"
                    class="absolute inset-0 z-50 flex items-center justify-center bg-black/80">
                    <p class="text-green-400 text-2xl md:text-3xl font-medium text-center px-8 max-w-3xl">
                        {{ displayedVictoryText }}
                    </p>
                </div>
            </div>

            <!-- BOTTOM: Camera Area (30%) - Always mounted, visibility controlled by showCamera -->
            <div v-show="showCamera" class="relative w-full h-[30%] bg-neutral-900 overflow-hidden">
                <BattleFrontCamera v-if="pureRole" :role="pureRole" :backend-url="config.public.backendUrl"
                    :state="battleState" class="w-full h-full" />
                <div v-else class="absolute inset-0 flex items-center justify-center text-white/30 text-sm">
                    📷 Rôle non défini (ajouter ?role=dream ou ?role=nightmare)
                </div>
            </div>

            <!-- Hidden camera for sending frames when UI is hidden -->
            <div v-if="!showCamera && pureRole" class="hidden">
                <BattleFrontCamera :role="pureRole" :backend-url="config.public.backendUrl" :state="battleState" />
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch, nextTick } from 'vue';
import { io } from 'socket.io-client';
import BattleBoss from '~/components/battle/BattleBoss.vue';
import BattleHUD from '~/components/battle/BattleHUD.vue';
import { useBattleState } from '~/composables/useBattleState';
import { BATTLE_NARRATIVE, ATTACK_NARRATIVE } from '~/utils/battleConstants';

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

// --- NARRATIVE TEXT ---
const narrativeText = ref('');
const showNarrativeText = ref(false);
const narrativeTimeout = ref(null);

// Show narrative intro on APPEARING
watch(battleState, (newState, oldState) => {
    if (newState === 'APPEARING' && oldState === 'IDLE') {
        showNarrative(BATTLE_NARRATIVE.intro, 5000);
    }
});

// Show phase narrative on FIGHTING based on current attack
watch([battleState, currentAttack], ([state, attack]) => {
    if (state === 'FIGHTING' && attack && ATTACK_NARRATIVE[attack]) {
        showNarrative(ATTACK_NARRATIVE[attack], 4000);
    }
});

function showNarrative(text, duration) {
    // Clear previous timeout
    if (narrativeTimeout.value) {
        clearTimeout(narrativeTimeout.value);
    }
    narrativeText.value = text;
    showNarrativeText.value = true;
    narrativeTimeout.value = setTimeout(() => {
        showNarrativeText.value = false;
    }, duration);
}

// --- DRAWING FEEDBACK ---
const showDrawingFeedback = ref(false);
const isDrawingValid = ref(false);
const bothSidesValid = ref(false);
const waitingForImage = ref(false);
const isGenerating = ref(false);
let feedbackTimeout = null;

// Watch for counter validity changes - require BOTH sides
watch([dreamCounterValid, nightmareCounterValid], ([dreamValid, nightmareValid]) => {
    // Show individual feedback
    if (dreamValid || nightmareValid) {
        isDrawingValid.value = true;
        showDrawingFeedback.value = true;
        clearTimeout(feedbackTimeout);
        feedbackTimeout = setTimeout(() => {
            showDrawingFeedback.value = false;
        }, 2000);
    }
    
    // Check if BOTH sides are now valid
    if (dreamValid && nightmareValid) {
        console.log('[Battle] 🎯 BOTH sides detected correct counter! Showing loading bar...');
        bothSidesValid.value = true;
        waitingForImage.value = true;
        
        // Show validation feedback briefly, then switch to loading bar
        showDrawingFeedback.value = true;
        setTimeout(() => {
            showDrawingFeedback.value = false;
            isGenerating.value = true;
        }, 1000);
    }
});

// --- FLYING IMAGE ANIMATION ---
const flyingImage = ref(null);
const flyingImageRef = ref(null);
const flyingImageStyle = ref({ left: '50%', bottom: '35%' });

// Watch for generated images - only trigger when BOTH sides valid
watch([dreamDrawingImage, nightmareDrawingImage], ([dreamImg, nightmareImg]) => {
    const img = dreamImg || nightmareImg;
    
    // Only proceed if both sides detected correct counter AND we have a generated image
    if (img && bothSidesValid.value && waitingForImage.value) {
        console.log('[Battle] 🎨 Generated image received! Waiting 1s then launching animation...');
        waitingForImage.value = false;
        isGenerating.value = false;
        
        // Wait 1 second before starting the flying animation
        setTimeout(() => {
            triggerFlyingAnimation(img);
        }, 1000);
    }
});


function triggerFlyingAnimation(imageSrc) {
    flyingImage.value = imageSrc.startsWith('data:') ? imageSrc : `data:image/png;base64,${imageSrc}`;
    flyingImageStyle.value = { left: '50%', bottom: '35%', transform: 'translateX(-50%) scale(1)', opacity: '1' };
    
    nextTick(() => {
        setTimeout(() => {
            // Animate to center of screen (towards enemy)
            flyingImageStyle.value = { 
                left: '50%', 
                top: '30%', 
                transform: 'translateX(-50%) scale(0.3)', 
                opacity: '0',
                transition: 'all 1s ease-in-out'
            };
        }, 100);
        
        // After animation completes: clear image, reset state, and trigger attack to proceed
        setTimeout(() => {
            flyingImage.value = null;
            bothSidesValid.value = false;
            console.log('[Battle] ⚔️ Animation complete! Triggering attack to proceed...');
            
            // Emit to backend to signal attack (Sync)
            if (socket && socket.connected) {
                socket.emit('trigger_attack', {});
            }
            
            triggerAttack();
        }, 1200);
    });
}

// --- VICTORY MESSAGE ---
const showVictoryMessage = ref(false);
const displayedVictoryText = ref('');
const victoryFullText = BATTLE_NARRATIVE.victory;

watch(battleState, (newState) => {
    if (newState === 'WEAKENED') {
        showVictoryMessage.value = true;
        typewriterEffect(victoryFullText);
    } else {
        showVictoryMessage.value = false;
        displayedVictoryText.value = '';
    }
});

function typewriterEffect(text) {
    displayedVictoryText.value = '';
    let i = 0;
    const interval = setInterval(() => {
        if (i < text.length) {
            displayedVictoryText.value += text.charAt(i);
            i++;
        } else {
            clearInterval(interval);
        }
    }, 50);
}

// Watch for victory to stop music
watch(showVictoryMessage, (val) => {
    if (val) {
        // Wait for typewriter to roughly finish (text length * 50ms) + buffer
        const duration = victoryFullText.length * 50 + 1000;
        setTimeout(() => {
            console.log('[Battle] Victory narrative complete - Stopping music');
            if (hudRef.value) hudRef.value.pauseMusic();
        }, duration);
    }
});

// --- COMPUTED ---
const isEndState = computed(() => {
    return battleState.value === 'WEAKENED' || battleState.value === 'CAPTURED';
});

// Show camera when NOT in IDLE, OR when debugMode is enabled
const showCamera = computed(() => {
    return battleState.value !== 'IDLE' || debugMode.value;
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
    if (narrativeTimeout.value) clearTimeout(narrativeTimeout.value);
    if (feedbackTimeout) clearTimeout(feedbackTimeout);
});
</script>

<style scoped>
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
    animation: fadeIn 0.5s ease-out forwards;
}

.fly-to-enemy {
    transition: all 1.5s ease-in-out;
}

@keyframes loadingBar {
    0% { width: 0%; }
    100% { width: 100%; }
}

.animate-loading-bar {
    animation: loadingBar 3s ease-in-out infinite;
}
</style>
