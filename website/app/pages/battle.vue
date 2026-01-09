<template>
  <div class="fixed inset-0 bg-black flex flex-col overflow-hidden font-mono select-none" @click="unlockAudio">
    <!-- 1. VIDEO LAYER (Background) -->
    <video v-show="currentVideo && !videoError && battleState !== 'IDLE'" ref="videoRef"
      class="absolute inset-0 w-full h-full object-cover z-0" :src="currentVideo" autoplay loop muted playsinline
      @error="handleVideoError" @loadeddata="onVideoLoaded">
    </video>
    <!-- 2. IDLE STATE (Waiting Screen) -->
    <div v-if="battleState === 'IDLE'"
      class="absolute inset-0 z-10 flex flex-col items-center justify-center bg-[#0a0a0a]">
      <div class="grid place-items-center gap-6">
        <div
          class="relative w-32 h-32 border-4 border-purple-500/30 rounded-full animate-pulse flex items-center justify-center">
          <div class="w-24 h-24 border-2 border-purple-500/60 rounded-full"></div>
          <div class="absolute w-full h-[2px] bg-purple-500 animate-[scan_2s_ease-in-out_infinite] opacity-50"></div>
        </div>
        <div class="text-center space-y-2">
          <h1 class="text-4xl font-black tracking-[0.2em] text-purple-400 glitch-text">
            BATAILLE FINALE
          </h1>
          <p class="text-sm tracking-widest opacity-70 uppercase text-purple-300">
            EN ATTENTE DES AGENTS
          </p>
        </div>
      </div>
    </div>
    <!-- 3. BATTLE UI OVERLAY (Active Game) -->
    <div v-if="battleState !== 'IDLE'" class="absolute inset-0 z-10 pointer-events-none">
      <BattleHUD ref="hudRef" :is-connected="isConnected" :show-debug="showDebug" :state="battleState" :hp="currentHp"
        :round="currentRound" :attack="currentAttack" :video-name="currentVideo?.split('/').pop() || 'None'"
        :current-music="currentMusic" :should-loop="musicShouldLoop" @simulate="simulateRecon"
        @capture="simulateCapture" />
      <BattleBoss v-if="battleState !== 'WEAKENED' && battleState !== 'CAPTURED'" :is-hit="isHit"
        :attack="currentAttack" />
      <BattleAgent v-if="battleState !== 'WEAKENED' && battleState !== 'CAPTURED'" :dream-valid="dreamCounterValid"
        :nightmare-valid="nightmareCounterValid" :is-attacking="isAttacking" :drawing-data="drawingData"
        @attack="triggerDevAttack" />
      <BattleState :message="stateMessage" :sub-message="stateSubMessage" :message-class="stateMessageClass" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue';
import BattleHUD from '~/components/battle/BattleHUD.vue';
import BattleBoss from '~/components/battle/BattleBoss.vue';
import BattleAgent from '~/components/battle/BattleAgent.vue';
import BattleState from '~/components/battle/BattleState.vue';
import { useBattleAttacks } from '~/composables/useBattleAttacks';

definePageMeta({ layout: false });

// --- COMPOSABLES ---
const { isConnected, lastPayload, connect, send } = useRiftSocket();
const { currentAttack, getNextAttack, resetAttacks } = useBattleAttacks();
// --- STATE ---
const battleState = ref('IDLE');
const currentHp = ref(5);
const currentRound = ref(0);
const currentVideo = ref(null);
const drawingData = ref(null);
const isAttacking = ref(false);
const isHit = ref(false);

const videoError = ref(false);
const videoRef = ref(null);
const hudRef = ref(null);
const audioUnlocked = ref(false);
const showDebug = ref(true);
const isSimulating = ref(false);
const currentMusic = ref(null);
const musicShouldLoop = ref(true);

// Counters
const dreamCounterValid = ref(false);
const nightmareCounterValid = ref(false);

const canTriggerAttack = computed(() => {
  return (dreamCounterValid.value || nightmareCounterValid.value) && !isAttacking.value;
});

// Messages
const stateMessage = ref(null);
const stateSubMessage = ref(null);
const stateMessageClass = ref('');

// --- CONSTANTS ---
const BATTLE_VIDEOS = {
  idle: null,
  appearing: '/battle-workshop/video-battle-appearing.mp4',
  fighting: '/battle-workshop/video-battle-fighting.mp4',
  hit: '/battle-workshop/video-battle-hit.mp4',
  weakened: '/battle-workshop/video-battle-weakened.mp4',
  captured: '/battle-workshop/video-battle-captured.mp4'
};
const BATTLE_MUSIC = {
  idle: null,
  appearing: '/battle-workshop/music-battle-intro.mp3',
  fighting: '/battle-workshop/music-battle-combat.mp3',
  hit: null,
  weakened: '/battle-workshop/music-battle-weakened.mp3',
  captured: '/battle-workshop/music-battle-victory.mp3'
};
const BATTLE_SFX = {
  hit: '/battle-workshop/sfx-battle-hit.mp3'
};

// --- METHODS ---
function unlockAudio() {
  // Music autoplays muted, this just ensures video plays
  if (!audioUnlocked.value && videoRef.value) {
    console.log('[Audio] Attempting to play video...');
    videoRef.value.play()
      .then(() => {
        audioUnlocked.value = true;
        console.log('[Audio] Video playing');
      })
      .catch(e => console.log("Video play failed:", e));
  }
}

function handleVideoError(e) {
  console.warn(`[Battle] Failed to load video: ${currentVideo.value}`);
  videoError.value = true;
}

function onVideoLoaded() {
  videoError.value = false;
}

function displayMessage(title, subtitle = null, cssClass = '') {
  stateMessage.value = title;
  stateSubMessage.value = subtitle;
  stateMessageClass.value = cssClass;
}

function clearMessage() {
  stateMessage.value = null;
  stateSubMessage.value = null;
}

// --- SIMULATION LOGIC ---
function simulateRecon() {
  console.log('[Dev] Enabling Simulation Mode');
  isSimulating.value = true;

  dreamCounterValid.value = true;
  nightmareCounterValid.value = true;
  if (!drawingData.value) drawingData.value = 'https://via.placeholder.com/600x400/000000/FFFFFF?text=AGENT+IMAGE';
}


function simulateCapture() {
  console.log('[Dev] Simulating Capture (Seal Placement)');
  isSimulating.value = true;

  // Send CAPTURED state to server
  if (send) {
    send({
      device_id: 'boss-workshop-website',
      battle_state: 'CAPTURED'
    });
  }
}


// --- DEV ATTACK TRIGGER ---

function triggerDevAttack() {
  if (!canTriggerAttack.value) return;

  console.log('[Dev] Attack button pressed - sending HIT to server');

  const nextHp = currentHp.value - 1;
  const currentAttackVal = currentAttack.value;

  // 1. Send HIT state + Updated HP
  if (send) {
    send({
      device_id: 'boss-workshop-website',
      battle_state: 'HIT',
      battle_boss_hp: nextHp,
      battle_boss_attack: currentAttackVal
    });
  }

  // 2. After 1 second, server/logic decides next state (FIGHTING or WEAKENED)
  setTimeout(() => {
    if (nextHp <= 0) {
      // Boss is weakened
      if (send) {
        send({
          device_id: 'boss-workshop-website',
          battle_state: 'WEAKENED',
          battle_boss_hp: 0,
          battle_boss_attack: null,
          battle_video_play: 'video-battle-weakened.mp4',
          battle_music_play: 'music-battle-weakened.mp3'
        });
      }
    } else {
      // Boss continues fighting -> New Attack
      const newAttack = getNextAttack(); // Updates currentAttack ref

      if (send) {
        send({
          device_id: 'boss-workshop-website',
          battle_state: 'FIGHTING',
          battle_boss_hp: nextHp,
          battle_boss_attack: newAttack,
          battle_video_play: 'video-battle-fighting.mp4',
          battle_music_play: 'music-battle-combat.mp3'
        });
      }
    }

    // Reset counters (local UI only)
    dreamCounterValid.value = false;
    nightmareCounterValid.value = false;
    drawingData.value = null;
  }, 1000);
}



// --- PAYLOAD HANDLER ---
// Handler for real WebSocket payloads
function handleServerPayload(payload) {
  if (!payload) return;

  console.log('[Battle] Received payload:', payload);

  // START CONDITION
  if (battleState.value === 'IDLE' && payload.rift_part_count === 4) {
    console.log('[Battle] Start Condition Met (4 Parts)');
    
    // Immediately reply to server with APPEARING state
    if (send) {
      send({
        ...payload, // Keep all existing payload data
        device_id: 'boss-workshop-website',
        battle_state: 'APPEARING',
        battle_boss_hp: 5,
        battle_boss_attack: null,
        battle_video_play: 'video-battle-appearing.mp4',
        battle_music_play: 'music-battle-intro.mp3'
      });
    }
    
    battleState.value = 'APPEARING';
    handleStateTransition('APPEARING');
    return; // Stop processing to let transition finish
  }

  // Sync State
  if (payload.battle_state) {
    const newState = payload.battle_state;
    if (newState !== battleState.value) {
      battleState.value = newState;
      handleStateTransition(newState);
    }
  }

  // Sync HP
  // Look for battle_boss_hp (new standard) OR battle_hp (legacy)
  if (payload.battle_boss_hp !== undefined) {
    currentHp.value = payload.battle_boss_hp;
  } else if (payload.battle_hp !== undefined) {
    currentHp.value = payload.battle_hp;
  }

  // Sync Round
  if (payload.battle_round !== undefined) {
    currentRound.value = payload.battle_round;
  }

  // Sync Attack
  // Look for battle_boss_attack (new standard) OR battle_attack (legacy)
  if (payload.battle_boss_attack !== undefined) {
    currentAttack.value = payload.battle_boss_attack;
  } else if (payload.battle_attack !== undefined) {
    currentAttack.value = payload.battle_attack;
  }

  // Validation counters
  if (!isSimulating.value) {
    if (payload.battle_counter_valid_parent !== undefined) dreamCounterValid.value = payload.battle_counter_valid_parent;
    if (payload.battle_counter_valid_child !== undefined) nightmareCounterValid.value = payload.battle_counter_valid_child;
  }

  // Sync Drawing Data
  if (payload.battle_drawing_data) drawingData.value = payload.battle_drawing_data;
  if (payload.battle_drawing_nightmare_image) drawingData.value = payload.battle_drawing_nightmare_image;
  if (payload.battle_drawing_dream_image) drawingData.value = payload.battle_drawing_dream_image;

  // Music override from server
  if (payload.battle_music_play) {
    const filename = payload.battle_music_play.startsWith('/')
      ? payload.battle_music_play
      : `/battle-workshop/music-${payload.battle_music_play}.mp3`;

    currentMusic.value = filename;
    if (hudRef.value && audioUnlocked.value) {
      hudRef.value.playMusic();
    }
  }
}

// Watch real WebSocket payloads
watch(lastPayload, (payload) => {
  handleServerPayload(payload);
}, { deep: true });

function handleStateTransition(state) {
  clearMessage();
  console.log(`[Battle] State transition to: ${state}`);
  switch (state) {
    case 'APPEARING':
      currentVideo.value = BATTLE_VIDEOS.appearing;
      currentMusic.value = BATTLE_MUSIC.appearing;
      musicShouldLoop.value = true;
      console.log('[Music] Setting APPEARING music:', currentMusic.value);
      if (hudRef.value && audioUnlocked.value) {
        console.log('[Music] Playing APPEARING music');
        hudRef.value.playMusic();
      } else {
        console.warn('[Music] Cannot play - hudRef:', !!hudRef.value, 'audioUnlocked:', audioUnlocked.value);
      }
      setTimeout(() => {
        if (battleState.value === 'APPEARING') {
          console.log('[Battle] Intro finished, starting fight...');
          const firstAttack = getNextAttack(); // Updates currentAttack ref
          if (send) {
            send({
              device_id: 'boss-workshop-website',
              battle_state: 'FIGHTING',
              battle_boss_hp: 5,
              battle_boss_attack: firstAttack,
              battle_video_play: 'video-battle-fighting.mp4',
              battle_music_play: 'music-battle-combat.mp3'
            });
          }
        }
      }, 10000); // 10 seconds for APPEARING
      break;
    case 'FIGHTING':
      currentVideo.value = BATTLE_VIDEOS.fighting;
      currentMusic.value = BATTLE_MUSIC.fighting;
      musicShouldLoop.value = true;
      console.log('[Music] Setting FIGHTING music:', currentMusic.value);
      if (hudRef.value && audioUnlocked.value) {
        console.log('[Music] Playing FIGHTING music');
        hudRef.value.playMusic();
      }
      break;
    case 'HIT':
      displayMessage('HIT', null, 'text-red-500 animate-pulse');
      currentVideo.value = BATTLE_VIDEOS.hit;
      // Keep fighting music but lower volume and play hit SFX over it
      if (hudRef.value && audioUnlocked.value) {
        hudRef.value.lowerMusicVolume();
        hudRef.value.playSFX(BATTLE_SFX.hit);
      }
      setTimeout(() => {
        if (hudRef.value) hudRef.value.restoreMusicVolume();
      }, 2000);
      break;
    case 'WEAKENED':
      displayMessage("L'ÉTRANGER EST AFFAIBLI", "Utilisez les sceaux de confinement de la BRC pour le mettre hors d'état de nuire !", 'text-purple-400');
      currentVideo.value = BATTLE_VIDEOS.weakened;
      currentMusic.value = BATTLE_MUSIC.weakened;
      musicShouldLoop.value = true;
      currentAttack.value = null; // Clear attack when weakened
      console.log('[Music] Setting WEAKENED music:', currentMusic.value);
      if (hudRef.value && audioUnlocked.value) {
        console.log('[Music] Playing WEAKENED music');
        hudRef.value.playMusic();
      }
      break;
    case 'CAPTURED':
      displayMessage('MENACE NEUTRALISÉE', null, 'text-green-400');
      currentVideo.value = BATTLE_VIDEOS.captured;
      currentMusic.value = BATTLE_MUSIC.captured;
      musicShouldLoop.value = false; // Victory music plays once
      currentAttack.value = null; // Clear attack when captured
      console.log('[Music] Setting CAPTURED music (no loop):', currentMusic.value);
      if (hudRef.value && audioUnlocked.value) {
        console.log('[Music] Playing CAPTURED music');
        hudRef.value.playMusic();
      }
      break;
  }
}

onMounted(() => {
  connect();
  console.log('[Battle] Component mounted, hudRef ready:', !!hudRef.value);
  // Wait a bit for child components to mount
  setTimeout(() => {
    console.log('[Battle] After timeout, hudRef ready:', !!hudRef.value);
  }, 100);
});


// Removed watchers to prevent double sending. 
// State changes are now driven explicitly by logic methods (triggerDevAttack, etc.)

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

  15% {
    transform: skewX(0deg);
    opacity: 1;
  }

  100% {
    transform: skewX(0deg);
    opacity: 1;
  }
}
</style>
