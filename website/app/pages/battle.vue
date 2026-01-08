<template>
  <div 
    class="fixed inset-0 bg-black flex flex-col overflow-hidden font-mono select-none"
    @click="unlockAudio"
  >
    <!-- 1. VIDEO LAYER (Background) -->
    <!-- Displays the current battle state loop video centered and covering the screen -->
    <video
      v-show="currentVideo && !videoError && battleState !== 'IDLE'"
      ref="videoRef"
      class="absolute inset-0 w-full h-full object-cover z-0"
      :src="currentVideo"
      autoplay
      loop
      muted
      playsinline
      @error="handleVideoError"
      @loadeddata="onVideoLoaded"
    ></video>

    <!-- 2. IDLE STATE (Waiting Screen) -->
    <div v-if="battleState === 'IDLE'" class="absolute inset-0 z-10 flex flex-col items-center justify-center bg-[#0a0a0a]">
      <div class="grid place-items-center gap-6">
        <!-- Pulse Animation -->
        <div class="relative w-32 h-32 border-4 border-purple-500/30 rounded-full animate-pulse flex items-center justify-center">
          <div class="w-24 h-24 border-2 border-purple-500/60 rounded-full"></div>
          <div class="absolute w-full h-[2px] bg-purple-500 animate-[scan_2s_ease-in-out_infinite] opacity-50"></div>
        </div>
        <!-- Title and Status -->
        <div class="text-center space-y-2">
          <h1 class="text-4xl font-black tracking-[0.2em] text-purple-400 glitch-text">
            BATAILLE FINALE
          </h1>
          <p class="text-sm tracking-widest opacity-70 uppercase text-purple-300">
            EN ATTENTE DES AGENTS
          </p>
          <div class="flex items-center justify-center gap-2 mt-4">
             <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
             <p class="text-xs text-purple-400">CONNEXION ÉTABLIE</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. BATTLE UI OVERLAY (Active Game) -->
    <!-- Only visible when NOT in IDLE state -->
    <div v-if="battleState !== 'IDLE'" class="absolute inset-0 z-10 pointer-events-none">
      
      <!-- HUD Component (Top + Debug) -->
      <BattleHUD 
        :is-connected="isConnected"
        :show-debug="showDebug"
        :state="battleState"
        :hp="currentHp"
        :round="currentRound"
        :attack="currentAttack"
        :video-name="currentVideo?.split('/').pop() || 'None'"
        @simulate="simulateRecon"
        @capture="simulateCapture"
      />

      <!-- Boss Component (Center) -->
      <BattleBoss 
        :is-hit="isHit"
        :attack="currentAttack"
      />

      <!-- Controls Component (Bottom) -->
      <BattleControls 
        :dream-valid="parentCounterValid"
        :nightmare-valid="childCounterValid"
        :is-attacking="isAttacking"
        :drawing-data="drawingData"
        @attack="triggerDevAttack"
      />

      <!-- OVERLAY MESSAGES (Success/Fail/Info) -->
      <transition name="fade">
        <div v-if="stateMessage" class="absolute inset-0 z-50 flex flex-col items-center justify-center bg-black/80 backdrop-blur-sm pointer-events-none">
          <h1 class="text-5xl md:text-7xl font-black text-white mb-6 text-center" :class="stateMessageClass">
            {{ stateMessage }}
          </h1>
          <p v-if="stateSubMessage" class="text-xl md:text-2xl text-white/70 max-w-2xl text-center leading-relaxed">
            {{ stateSubMessage }}
          </p>
        </div>
      </transition>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue';
import BattleHUD from '~/components/battle/BattleHUD.vue';
import BattleBoss from '~/components/battle/BattleBoss.vue';
import BattleControls from '~/components/battle/BattleControls.vue';

definePageMeta({ layout: false });

// --- COMPOSABLES ---
const { isConnected, lastPayload, connect } = useRiftSocket();

// --- STATE ---
const battleState = ref('IDLE'); // IDLE, APPEARING, FIGHTING, HIT, WEAKENED, CAPTURED, DONE
const currentHp = ref(5);
const currentRound = ref(0);
const currentAttack = ref(null);
const currentVideo = ref(null);
const drawingData = ref(null);
const isAttacking = ref(false);
const isHit = ref(false); // For boss shake animation

const videoError = ref(false);
const videoRef = ref(null);
const audioUnlocked = ref(false);
const showDebug = ref(true);
const isSimulating = ref(false); // Flag to prevent socket from overriding sim

// Counters
const parentCounterValid = ref(false);
const childCounterValid = ref(false);

const canTriggerAttack = computed(() => {
  return (parentCounterValid.value || childCounterValid.value) && !isAttacking.value;
});

// Messages
const stateMessage = ref(null);
const stateSubMessage = ref(null);
const stateMessageClass = ref('');

// --- CONSTANTS ---
const ATTACK_COUNTERS = {
  lightning: 'bouclier',
  fire: 'eau',
  ice: 'feu',
  shadow: 'lumière',
  void: 'épée'
};

const BATTLE_VIDEOS = {
  idle: null,
  appearing: '/video-battle-appearing.mp4',
  fighting: '/video-battle-fighting.mp4',
  hit: '/video-battle-hit.mp4',
  weakened: '/video-battle-weakened.mp4',
  captured: '/video-battle-captured.mp4'
};

// --- METHODS ---

function getCounterFor(attack) {
  return ATTACK_COUNTERS[attack] || attack;
}

function unlockAudio() {
  if (!audioUnlocked.value && videoRef.value) {
    videoRef.value.play()
      .then(() => { audioUnlocked.value = true; })
      .catch(e => console.log("Audio unlock needed:", e));
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
  
  // Mock receiving valid recognition from both cameras
  parentCounterValid.value = true;
  childCounterValid.value = true;
  // If no art, put a placeholder so we see the animation
  if (!drawingData.value) drawingData.value = 'https://via.placeholder.com/600x400/000000/FFFFFF?text=AGENT+IMAGE';
}

function simulateCapture() {
  console.log('[Dev] Simulating Capture (Seal Placement)');
  isSimulating.value = true;
  
  // Directly transition to CAPTURED since we don't have server feedback for this mock
  battleState.value = 'CAPTURED';
  handleStateTransition('CAPTURED');
  
  // Mock final completion after a delay
  setTimeout(() => {
    battleState.value = 'DONE';
    handleStateTransition('DONE');
  }, 4000);
}

function triggerDevAttack() {
  if (!canTriggerAttack.value) return;

  console.log('[Dev] Global Attack Triggered!');
  
  // 1. Animation: Agent Picture moves to center
  isAttacking.value = true;

  // 2. Impact moment (after travel time)
  setTimeout(() => {
    // 3. Boss takes hit
    isHit.value = true;
    displayMessage('HIT !', null, 'text-red-500 animate-pulse');
    
    // Reduce HP
    if (currentHp.value > 0) currentHp.value--;

    // 4. Reset
    setTimeout(() => {
      isAttacking.value = false;
      isHit.value = false;
      clearMessage();
      
      // Next Round Logic (Mock)
      currentRound.value++;
      
      // Reset validation (unless manual sim override needed?)
      // If we are simulating, maybe we want to force re-click? 
      // Let's reset them to force user to click simulate again or wait for logic
      parentCounterValid.value = false;
      childCounterValid.value = false;
      isSimulating.value = false; // Reset sim mode to allow new real data or new sim
      
      if (currentHp.value <= 0) {
        battleState.value = 'WEAKENED';
        handleStateTransition('WEAKENED');
      } else {
        // Change attack for variety
        const attacks = Object.keys(ATTACK_COUNTERS);
        currentAttack.value = attacks[currentRound.value % attacks.length];
      }
      
    }, 1000); // Wait for hit impact
  }, 600); // Travel time
}


// --- PAYLOAD HANDLER ---
watch(lastPayload, (payload) => {
  if (!payload) return;

  // 1. Auto-Start Logic
  if (battleState.value === 'IDLE' && payload.rift_part_count === 4) {
    console.log('[Battle] Start Condition Met (4 Parts)');
    battleState.value = 'APPEARING';
    handleStateTransition('APPEARING'); // Ensure logic runs
  }
  
  // 2. Battle State Updates
  if (payload.battle_state) {
    const newState = payload.battle_state.toUpperCase();
    if (newState !== battleState.value) {
      battleState.value = newState;
      handleStateTransition(newState);
    }
  }

  // 3. Data Updates
  if (payload.battle_hp !== undefined) currentHp.value = payload.battle_hp;
  if (payload.battle_round !== undefined) currentRound.value = payload.battle_round;
  
  if (payload.battle_attack) {
    currentAttack.value = payload.battle_attack;
    
    // Reset counters on new attack ONLY if not simulating
    if (!isSimulating.value) {
       childCounterValid.value = false;
       parentCounterValid.value = false;
    }
  }
  
  // Only update validation from payload IF NOT simulating
  if (!isSimulating.value) {
    if (payload.battle_counter_valid_parent !== undefined) parentCounterValid.value = payload.battle_counter_valid_parent;
    if (payload.battle_counter_valid_child !== undefined) childCounterValid.value = payload.battle_counter_valid_child;
  }

  // 4. Image Handling
  if (payload.battle_drawing_data) drawingData.value = payload.battle_drawing_data;
  if (payload.battle_drawing_nightmare_image) drawingData.value = payload.battle_drawing_nightmare_image;
  if (payload.battle_drawing_dream_image) drawingData.value = payload.battle_drawing_dream_image;

  // 5. Hit Animation Trigger
  if (payload.battle_hit_confirmed) {
    triggerAttackAnimation();
  }

  // Debug: Direct Video Override
  if (payload.battle_video_play) {
    const filename = payload.battle_video_play.startsWith('/') ? payload.battle_video_play : `/${payload.battle_video_play}`;
    currentVideo.value = filename;
  }

}, { deep: true });

function handleStateTransition(state) {
  clearMessage();
  switch (state) {
    case 'APPEARING':
      currentVideo.value = BATTLE_VIDEOS.appearing;
      // MOCK: Auto-switch to fighting after 5s
      setTimeout(() => {
        if (battleState.value === 'APPEARING') {
          console.log('[Mock] Auto-transition to FIGHTING');
          battleState.value = 'FIGHTING';
          currentVideo.value = BATTLE_VIDEOS.fighting;
          currentAttack.value = 'lightning';
          currentRound.value = 1;
        }
      }, 5000);
      break;
    case 'FIGHTING':
      currentVideo.value = BATTLE_VIDEOS.fighting;
      break;
    case 'HIT':
      displayMessage('HIT!', null, 'text-yellow-400 animate-pulse');
      currentVideo.value = BATTLE_VIDEOS.hit;
      setTimeout(clearMessage, 2000);
      break;
    case 'WEAKENED':
      displayMessage("L'ÉTRANGER EST AFFAIBLIS", "Utilisez les sceaux de confinement de la BRC pour le mettre hors d'état de nuire !", 'text-purple-400');
      currentVideo.value = BATTLE_VIDEOS.weakened;
      break;
    case 'CAPTURED':
      displayMessage('MENACE NEUTRALISÉE', null, 'text-green-400');
      currentVideo.value = BATTLE_VIDEOS.captured;
      break;
    case 'DONE':
      displayMessage('VICTOIRE', 'La faille est refermée.', 'text-green-400');
      break;
  }
}

function triggerAttackAnimation() {
  isAttacking.value = true;
  setTimeout(() => { isAttacking.value = false; }, 1000);
}

// --- LIFECYCLE ---
onMounted(() => {
  connect();
});
</script>

<style scoped>
/* Custom animations */
@keyframes scan {
  0% { top: 0%; opacity: 0; }
  50% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

.glitch-text {
  text-shadow: 2px 0 #a855f7, -2px 0 #06b6d4;
  animation: glitch 3s infinite alternate-reverse;
}

@keyframes glitch {
  0% { transform: skewX(0deg); opacity: 1; }
  5% { transform: skewX(10deg); opacity: 0.8; }
  10% { transform: skewX(-10deg); opacity: 1; }
  15% { transform: skewX(0deg); opacity: 1; }
  100% { transform: skewX(0deg); opacity: 1; }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
