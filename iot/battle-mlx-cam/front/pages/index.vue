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
                <!-- Video Layer -->
                <video v-show="currentVideo && !videoError" ref="videoRef"
                    class="absolute inset-0 w-full h-full object-cover z-0" 
                    :src="currentVideo" autoplay loop muted playsinline 
                    @error="handleVideoError" @loadeddata="onVideoLoaded" />

                <!-- IDLE BG -->
                <div v-if="battleState === 'IDLE' || !currentVideo"
                    class="absolute inset-0 z-10 bg-black flex items-center justify-center">
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
import { computed, onMounted, onUnmounted, ref } from 'vue';
import BattleBoss from '~/components/battle/BattleBoss.vue';
import BattleHUD from '~/components/battle/BattleHUD.vue';
import { useBattleState } from '~/composables/useBattleState';

// --- CONFIG ---
const config = useRuntimeConfig();
const route = useRoute();

// Role from URL query param only (no selector screen)
const selectedRole = ref(route.query.role || null);

// Debug mode from localStorage
const debugMode = ref(false);

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

// --- COMPUTED ---
const isEndState = computed(() => {
    return battleState.value === 'WEAKENED' || battleState.value === 'CAPTURED';
});

// Show camera when NOT idle, OR when debugMode is enabled
const showCamera = computed(() => {
    return battleState.value !== 'IDLE' || debugMode.value;
});

// --- LIFECYCLE ---
onMounted(() => {
    // Load debug mode from config
    const savedDebug = localStorage.getItem('battle_debug_mode');
    if (savedDebug) {
        try { debugMode.value = JSON.parse(savedDebug); } catch {}
    }
    
    init();
});
</script>
