<template>
  <div 
    class="fixed inset-0 bg-black flex flex-col overflow-hidden font-mono select-none"
    @click="handleClick"
  >
    <!-- Video Layer (Full Screen Background) -->
    <video
      v-show="currentVideo && !videoError && battleState !== 'IDLE'"
      ref="videoRef"
      class="absolute inset-0 w-full h-full object-cover"
      :src="currentVideo"
      autoplay
      loop
      muted
      playsinline
      @error="handleVideoError"
      @loadeddata="onVideoLoaded"
    ></video>

    <!-- IDLE State - Waiting Screen -->
    <div v-if="battleState === 'IDLE'" class="absolute inset-0 z-10 flex flex-col items-center justify-center bg-[#0a0a0a]">
      <div class="grid place-items-center gap-6">
        <div class="relative w-32 h-32 border-4 border-purple-500/30 rounded-full animate-pulse flex items-center justify-center">
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
          <p class="text-xs text-purple-400 mt-4 bg-purple-500/10 px-4 py-2 rounded border border-purple-500/20 animate-pulse">
            ÉCOUTE SUR PORT 81
          </p>
        </div>
      </div>
    </div>

    <!-- Battle UI Overlay -->
    <div v-if="battleState !== 'IDLE'" class="absolute inset-0 z-20 flex flex-col pointer-events-none">
      
      <!-- Top: Agent Zone (Drawing Display) -->
      <div class="flex-1 flex items-center justify-center p-8">
        <div v-if="drawingData" class="drawing-container relative">
          <img 
            :src="drawingData" 
            class="max-w-full max-h-[40vh] object-contain rounded-lg shadow-2xl"
            :class="{'animate-attack': isAttacking}"
          />
        </div>
        <div v-else class="text-white/20 text-2xl uppercase tracking-widest">
          Zone Agent
        </div>
      </div>

      <!-- Middle: Boss Zone + Health Bar -->
      <div class="flex flex-col items-center py-4">
        <!-- Health Bar -->
        <div class="w-[80%] max-w-xl mb-4">
          <div class="flex items-center gap-2 mb-2">
            <span class="text-red-400 text-xs uppercase tracking-wider">HP</span>
            <span class="text-white/50 text-xs">{{ currentHp }}/5</span>
          </div>
          <div class="flex gap-1">
            <div 
              v-for="i in 5" 
              :key="i"
              class="flex-1 h-4 rounded transition-all duration-500"
              :class="i <= currentHp ? 'bg-gradient-to-r from-red-600 to-red-400 shadow-[0_0_10px_rgba(239,68,68,0.5)]' : 'bg-gray-800'"
            ></div>
          </div>
        </div>

        <!-- Boss Name -->
        <div class="text-center">
          <h2 class="text-3xl font-black text-white tracking-wider">L'ÉTRANGER</h2>
          <p v-if="currentAttack" class="text-yellow-400 text-sm mt-1 animate-pulse">
            Attaque : {{ currentAttack.toUpperCase() }}
          </p>
        </div>
      </div>

      <!-- Bottom: Counter Zone -->
      <div class="flex-1 flex items-center justify-center p-8">
        <div v-if="currentAttack" class="text-center">
          <p class="text-white/60 text-lg mb-2">Contrez avec :</p>
          <div class="text-4xl font-bold text-cyan-400 animate-bounce">
            {{ getCounterFor(currentAttack)?.toUpperCase() }}
          </div>
          <div class="mt-4 flex gap-4 justify-center">
            <div 
              class="px-4 py-2 rounded-lg border transition-all"
              :class="parentCounterValid ? 'border-blue-500 bg-blue-500/20 text-blue-400' : 'border-gray-700 text-gray-500'"
            >
              <span class="text-xs uppercase">Parent</span>
              <span v-if="parentCounterValid" class="ml-2">✓</span>
            </div>
            <div 
              class="px-4 py-2 rounded-lg border transition-all"
              :class="childCounterValid ? 'border-pink-500 bg-pink-500/20 text-pink-400' : 'border-gray-700 text-gray-500'"
            >
              <span class="text-xs uppercase">Enfant</span>
              <span v-if="childCounterValid" class="ml-2">✓</span>
            </div>
          </div>
        </div>
      </div>

      <!-- State Messages -->
      <div v-if="stateMessage" class="absolute inset-0 flex items-center justify-center bg-black/60 z-30">
        <div class="text-center animate-fadeIn">
          <h1 class="text-5xl font-black text-white mb-4" :class="stateMessageClass">
            {{ stateMessage }}
          </h1>
          <p v-if="stateSubMessage" class="text-xl text-white/70 animate-[fadeIn_0.5s_ease-out_0.5s_both]">
            {{ stateSubMessage }}
          </p>
        </div>
      </div>
    </div>

    <!-- Connection Status -->
    <div class="absolute top-4 right-4 z-50 bg-black/50 backdrop-blur-md px-4 py-2 rounded border border-white/10 flex items-center gap-3">
      <div 
        class="w-2 h-2 rounded-full transition-colors duration-500"
        :class="isConnected ? 'bg-[#33ff00] shadow-[0_0_10px_#33ff00]' : 'bg-red-500 animate-pulse'"
      ></div>
      <span class="text-[10px] tracking-wider uppercase opacity-50 text-white">
        {{ isConnected ? 'ONLINE' : 'OFFLINE' }}
      </span>
    </div>

    <!-- Debug Panel (Dev only) -->
    <div v-if="showDebug" class="absolute bottom-4 left-4 z-50 bg-black/80 p-4 rounded border border-white/20 text-xs text-white/60 font-mono">
      <div>State: {{ battleState }}</div>
      <div>HP: {{ currentHp }}/5</div>
      <div>Round: {{ currentRound }}/5</div>
      <div>Attack: {{ currentAttack }}</div>
      <div>Video: {{ currentVideo }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted, onUnmounted } from 'vue';

definePageMeta({ layout: false });

// WebSocket
const { isConnected, lastPayload, connect } = useRiftSocket();

// Battle State
const battleState = ref('IDLE'); // IDLE, APPEARING, FIGHTING, HIT, WEAKENED, CAPTURED, DONE
const currentHp = ref(5);
const currentRound = ref(0);
const currentAttack = ref(null);
const currentVideo = ref(null);
const drawingData = ref(null);
const videoError = ref(false);
const videoRef = ref(null);
const audioUnlocked = ref(false);
const showDebug = ref(true);
const isAttacking = ref(false);

// Counter validation
const parentCounterValid = ref(false);
const childCounterValid = ref(false);

// State messages
const stateMessage = ref(null);
const stateSubMessage = ref(null);
const stateMessageClass = ref('');

// Attack -> Counter mapping
const ATTACK_COUNTERS = {
  lightning: 'bouclier',
  fire: 'eau',
  ice: 'feu',
  shadow: 'lumière',
  void: 'épée'
};

function getCounterFor(attack) {
  return ATTACK_COUNTERS[attack] || attack;
}

// Video mapping
const BATTLE_VIDEOS = {
  idle: null,
  appearing: '/video-battle-appearing.mp4',
  fighting: '/video-battle-fighting.mp4',
  hit: '/video-battle-hit.mp4',
  weakened: '/video-battle-weakened.mp4',
  captured: '/video-battle-captured.mp4'
};

function handleClick() {
  if (!audioUnlocked.value && videoRef.value) {
    videoRef.value.play().catch(e => console.log("Audio unlock attempt", e));
    audioUnlocked.value = true;
  }
}

function handleVideoError(e) {
  console.warn(`[Battle] Failed to load video: ${currentVideo.value}`, e);
  videoError.value = true;
}

function onVideoLoaded() {
  videoError.value = false;
}

function showMessage(message, subMessage = null, cssClass = '') {
  stateMessage.value = message;
  stateSubMessage.value = subMessage;
  stateMessageClass.value = cssClass;
}

function clearMessage() {
  stateMessage.value = null;
  stateSubMessage.value = null;
}

// Main payload handler
watch(lastPayload, (payload) => {
  if (!payload) return;
  console.log('[Battle] Payload received:', payload);

  // Update battle state
  if (payload.battle_state) {
    const newState = payload.battle_state.toUpperCase();
    
    if (newState !== battleState.value) {
      battleState.value = newState;
      
      // Handle state transitions
      switch (newState) {
        case 'APPEARING':
          clearMessage();
          currentVideo.value = BATTLE_VIDEOS.appearing;
          break;
        case 'FIGHTING':
          clearMessage();
          currentVideo.value = BATTLE_VIDEOS.fighting;
          break;
        case 'HIT':
          showMessage('HIT!', null, 'text-yellow-400 animate-pulse');
          currentVideo.value = BATTLE_VIDEOS.hit;
          setTimeout(clearMessage, 2000);
          break;
        case 'WEAKENED':
          showMessage("L'Étranger est affaibli!", "Posez les cages sur les capteurs RFID", 'text-purple-400');
          currentVideo.value = BATTLE_VIDEOS.weakened;
          break;
        case 'CAPTURED':
          showMessage('Étranger vaincu!', null, 'text-green-400');
          currentVideo.value = BATTLE_VIDEOS.captured;
          break;
        case 'DONE':
          showMessage('Étranger vaincu!', 'Les derniers morceaux de faille sont dans les trappes des souches', 'text-green-400');
          break;
      }
    }
  }

  // Update HP
  if (payload.battle_hp !== undefined) {
    currentHp.value = payload.battle_hp;
  }

  // Update round
  if (payload.battle_round !== undefined) {
    currentRound.value = payload.battle_round;
  }

  // Update attack
  if (payload.battle_attack) {
    currentAttack.value = payload.battle_attack;
    parentCounterValid.value = false;
    childCounterValid.value = false;
  }

  // Update counter validation
  if (payload.battle_counter_valid_parent !== undefined) {
    parentCounterValid.value = payload.battle_counter_valid_parent;
  }
  if (payload.battle_counter_valid_child !== undefined) {
    childCounterValid.value = payload.battle_counter_valid_child;
  }

  // Update drawing data (legacy key)
  if (payload.battle_drawing_data) {
    drawingData.value = payload.battle_drawing_data;
    // Trigger attack animation when drawing is sent
    if (payload.battle_hit_confirmed) {
      isAttacking.value = true;
      setTimeout(() => { isAttacking.value = false; }, 1000);
    }
  }

  // NEW: Handle Nightmare camera image
  if (payload.battle_drawing_nightmare_image) {
    drawingData.value = payload.battle_drawing_nightmare_image;
    console.log('[Battle] Nightmare image received');
  }

  // NEW: Handle Dream camera image
  if (payload.battle_drawing_dream_image) {
    drawingData.value = payload.battle_drawing_dream_image;
    console.log('[Battle] Dream image received');
  }

  // Video override
  if (payload.battle_video_play) {
    const filename = payload.battle_video_play.startsWith('/') 
      ? payload.battle_video_play 
      : `/${payload.battle_video_play}`;
    currentVideo.value = filename;
  }

}, { deep: true });

onMounted(() => {
  connect();
});
</script>

<style scoped>
@keyframes scan {
  0% { top: 0%; opacity: 0; }
  50% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fadeIn {
  animation: fadeIn 0.5s ease-out forwards;
}

.glitch-text {
  text-shadow: 2px 0 #ff00ff, -2px 0 #00ffff;
  animation: glitch 1s infinite alternate-reverse;
}

@keyframes glitch {
  0% { text-shadow: 2px 0 #ff00ff, -2px 0 #00ffff; transform: skewX(0deg); }
  20% { text-shadow: -2px 0 #ff00ff, 2px 0 #00ffff; transform: skewX(5deg); }
  40% { text-shadow: 2px 0 #ff00ff, -2px 0 #00ffff; transform: skewX(-3deg); }
  60% { text-shadow: -2px 0 #ff00ff, 2px 0 #00ffff; transform: skewX(0deg); }
  100% { transform: skewX(0deg); }
}

@keyframes attack {
  0% { transform: translateY(0) scale(1); opacity: 1; }
  50% { transform: translateY(-100px) scale(1.2); opacity: 1; }
  100% { transform: translateY(-300px) scale(0.5); opacity: 0; }
}

.animate-attack {
  animation: attack 1s ease-out forwards;
}

.drawing-container {
  transition: all 0.3s ease;
}
</style>
