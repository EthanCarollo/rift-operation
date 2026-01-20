// Battle State Composable
// Handles all battle logic, state management, and server communication

import { ref, computed, watch } from 'vue';
import {
    DEVICE_ID,
    BATTLE_VIDEOS,
    BATTLE_MUSIC,
    BATTLE_SFX,
    BATTLE_STATE_CONFIG,
    APPEARING_DURATION,
    HIT_DURATION,
    VOLUME_RESTORE_DELAY,
    INITIAL_HP,
    START_CONDITION_PARTS,
    type BattleState,
} from '~/utils/battleConstants';
import { useBattleAttacks } from '~/composables/useBattleAttacks';

export function useBattleState(debug = false) {
    // --- COMPOSABLES ---
    const { isConnected, lastPayload, connect, send } = useRiftSocket();
    const { currentAttack, getNextAttack } = useBattleAttacks();
    // --- STATE ---
    const battleState = ref<BattleState>('IDLE');
    const currentHp = ref(INITIAL_HP);
    const currentVideo = ref<string | null>(null);
    const currentMusic = ref<string | null>(null);
    const musicShouldLoop = ref(true);
    const lastReceivedPayload = ref<any>(null);
    // UI State
    const dreamDrawingImage = ref<string | null>(null);
    const nightmareDrawingImage = ref<string | null>(null);
    const isAttacking = ref(false);
    const isHit = ref(false);
    const videoError = ref(false);
    const audioUnlocked = ref(false);
    // Counters
    const dreamCounterValid = ref(false);
    const nightmareCounterValid = ref(false);
    // Messages
    const stateMessage = ref<string | null>(null);
    const stateSubMessage = ref<string | null>(null);
    const stateMessageClass = ref('');
    // Refs (set by component)
    const hudRef = ref<any>(null);
    const videoRef = ref<any>(null);
    // --- COMPUTED ---
    const canTriggerAttack = computed(() => {
        return (dreamCounterValid.value || nightmareCounterValid.value) && !isAttacking.value;
    });
    // --- HELPERS ---
    function log(...args: any[]) {
        if (debug) console.log('[Battle]', ...args);
    }

    function displayMessage(title: string, subtitle: string | null = null, cssClass = '') {
        stateMessage.value = title;
        stateSubMessage.value = subtitle;
        stateMessageClass.value = cssClass;
    }

    function clearMessage() {
        stateMessage.value = null;
        stateSubMessage.value = null;
    }

    // Centralized send helper
    function sendBattlePayload(state: string, overrides: Record<string, any> = {}) {
        if (!send) return;

        const basePayload = lastReceivedPayload.value || {};
        const payload = {
            ...basePayload,
            device_id: DEVICE_ID,
            battle_state: state,
            battle_boss_hp: currentHp.value,
            battle_boss_attack: currentAttack.value,
            battle_video_play: BATTLE_VIDEOS[state] || null,
            battle_music_play: BATTLE_MUSIC[state]?.split('/').pop()?.replace('.mp3', '') || null,
            ...overrides
        };

        log('Sending payload:', state, payload);
        send(payload);
    }

    // --- STATE TRANSITIONS ---
    function handleStateTransition(state: string) {
        clearMessage();
        log('State transition to:', state);

        const config = BATTLE_STATE_CONFIG[state];
        if (!config) return;

        // Apply config
        if (config.video && config.video !== currentVideo.value) currentVideo.value = config.video;
        if (config.music) currentMusic.value = config.music;
        musicShouldLoop.value = config.loop;

        // Display message if defined
        if (config.message) {
            displayMessage(config.message, config.subMessage || null, config.messageClass || '');
        }

        // Clear attack if needed
        if (config.clearAttack) {
            currentAttack.value = null;
        }

        // Music Management
        if (hudRef.value && audioUnlocked.value) {
            if (config.music) {
                log('Playing music:', config.music);
                hudRef.value.playMusic();
            } else if (state === 'IDLE') {
                // Explicitly stop music for IDLE state
                log('IDLE state: Stopping music');
                hudRef.value.pauseMusic();
            }
            // If music is null but not IDLE (e.g. HIT), keep previous music playing
        }

        // State-specific logic
        if (state === 'APPEARING') {
            scheduleAutoFight();
        } else if (state === 'HIT') {
            handleHitEffects();
        }
    }

    function scheduleAutoFight() {
        setTimeout(() => {
            if (battleState.value === 'APPEARING') {
                log('Intro finished, sending FIGHTING to server...');
                // Use INITIAL_HP (5) to deterministically pick first attack
                const firstAttack = getNextAttack(INITIAL_HP);
                sendBattlePayload('FIGHTING', {
                    battle_boss_hp: INITIAL_HP,
                    battle_boss_attack: firstAttack
                });

                // Optimistic local update (don't wait for server echo)
                battleState.value = 'FIGHTING';
                handleStateTransition('FIGHTING');
            }
        }, APPEARING_DURATION);
    }

    function handleHitEffects() {
        if (hudRef.value && audioUnlocked.value) {
            hudRef.value.lowerMusicVolume();
            hudRef.value.playSFX(BATTLE_SFX.hit);
        }
        setTimeout(() => {
            if (hudRef.value) hudRef.value.restoreMusicVolume();
        }, VOLUME_RESTORE_DELAY);
    }

    // --- PAYLOAD HANDLER ---
    function handleServerPayload(payload: any) {
        if (!payload) return;

        log('Received payload:', payload);

        // START CONDITION
        if (battleState.value === 'IDLE' && payload.rift_part_count === START_CONDITION_PARTS) {
            log('Start Condition Met');
            lastReceivedPayload.value = payload;
            // Send ACTIVE then APPEARING
            sendBattlePayload('ACTIVE', { battle_boss_hp: null, battle_boss_attack: null });
            sendBattlePayload('APPEARING', { battle_boss_hp: INITIAL_HP, battle_boss_attack: null });
            battleState.value = 'APPEARING';
            handleStateTransition('APPEARING');
            return;
        }

        // Sync State
        if (payload.battle_state && payload.battle_state !== battleState.value) {
            battleState.value = payload.battle_state as BattleState;
            handleStateTransition(payload.battle_state);
        }

        // Sync HP
        if (payload.battle_boss_hp !== undefined) {
            currentHp.value = payload.battle_boss_hp;
        } else if (payload.battle_hp !== undefined) {
            currentHp.value = payload.battle_hp;
        }

        // Sync Attack
        if (payload.battle_boss_attack !== undefined) {
            currentAttack.value = payload.battle_boss_attack;
        } else if (payload.battle_attack !== undefined) {
            currentAttack.value = payload.battle_attack;
        }

        // Sync Counters
        // Sync Counters (Using correct JSON keys)
        if (payload.battle_drawing_dream_recognised !== undefined) {
            dreamCounterValid.value = payload.battle_drawing_dream_recognised;
        }
        if (payload.battle_drawing_nightmare_recognised !== undefined) {
            nightmareCounterValid.value = payload.battle_drawing_nightmare_recognised;
        }

        // Sync Drawing
        if (payload.battle_drawing_nightmare_image) nightmareDrawingImage.value = payload.battle_drawing_nightmare_image;
        if (payload.battle_drawing_dream_image) dreamDrawingImage.value = payload.battle_drawing_dream_image;
    }

    // --- ACTIONS ---
    function triggerAttack() {
        if (!canTriggerAttack.value) return;

        log('Attack triggered');
        const nextHp = currentHp.value - 1;

        // Optimistically update HP locally
        currentHp.value = nextHp;

        // Immediately reset valid counters to disable button
        dreamCounterValid.value = false;
        nightmareCounterValid.value = false;

        // Send HIT
        sendBattlePayload('HIT', { battle_boss_hp: nextHp });

        // Optimistic HIT update
        battleState.value = 'HIT';
        handleStateTransition('HIT');

        // After delay, send next state
        setTimeout(() => {
            if (nextHp <= 0) {
                sendBattlePayload('WEAKENED', { battle_boss_hp: 0, battle_boss_attack: null });
                // Optimistic WEAKENED update
                battleState.value = 'WEAKENED';
                handleStateTransition('WEAKENED');
            } else {
                // Deterministic attack based on next HP
                const newAttack = getNextAttack(nextHp);
                sendBattlePayload('FIGHTING', { battle_boss_hp: nextHp, battle_boss_attack: newAttack });
                // Optimistic FIGHTING update
                battleState.value = 'FIGHTING';
                handleStateTransition('FIGHTING');
            }
        }, HIT_DURATION);
    }

    function simulateCapture() {
        log('Simulating Capture');
        sendBattlePayload('CAPTURED', { battle_boss_attack: null });
        // Optimistic CAPTURED update
        battleState.value = 'CAPTURED';
        handleStateTransition('CAPTURED');
    }

    function simulateRecon() {
        log('Enabling Simulation Mode');
        dreamCounterValid.value = true;
        nightmareCounterValid.value = true;
        dreamCounterValid.value = true;
        nightmareCounterValid.value = true;
        if (!dreamDrawingImage.value) {
            dreamDrawingImage.value = 'https://via.placeholder.com/600x400/000000/FFFFFF?text=DREAM+IMAGE';
        }
        if (!nightmareDrawingImage.value) {
            nightmareDrawingImage.value = 'https://via.placeholder.com/600x400/000000/FFFFFF?text=NIGHTMARE+IMAGE';
        }
    }

    function unlockAudio() {
        if (!audioUnlocked.value && videoRef.value) {
            videoRef.value.play()
                .then(() => {
                    audioUnlocked.value = true;
                    log('Audio unlocked');
                })
                .catch((e: Error) => log('Audio unlock failed:', e.message));
        }
    }

    function handleVideoError() {
        log('Video load failed:', currentVideo.value);
        videoError.value = true;
    }

    function onVideoLoaded() {
        videoError.value = false;
    }

    // --- LIFECYCLE ---
    function init() {
        connect();
        log('Initialized');
    }

    // Watch payloads
    watch(lastPayload, (payload) => {
        handleServerPayload(payload);
    }, { deep: true });

    // --- EXPOSE ---
    return {
        // State
        battleState,
        currentHp,
        currentAttack,
        currentVideo,
        currentMusic,
        musicShouldLoop,

        dreamDrawingImage,
        nightmareDrawingImage,
        isAttacking,
        isHit,
        videoError,
        audioUnlocked,
        isConnected,

        // Counters
        dreamCounterValid,
        nightmareCounterValid,
        canTriggerAttack,

        // Messages
        stateMessage,
        stateSubMessage,
        stateMessageClass,

        // Refs (to be set by component)
        hudRef,
        videoRef,

        // Actions
        init,
        triggerAttack,
        simulateCapture,
        simulateRecon,
        unlockAudio,
        handleVideoError,
        onVideoLoaded
    };
}
