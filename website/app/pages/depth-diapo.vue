<template>
  <div
    class="fixed inset-0 overflow-hidden select-none"
    ref="containerRef"
  >
    <!-- Background from Figma -->
    <img
      src="/depth-diapo/background.svg"
      alt=""
      class="absolute inset-0 w-full h-full object-cover"
    />

    <!-- Main Content -->
    <div class="relative z-10 h-full flex flex-col items-center justify-center">
      
      <!-- Status bar -->
      <div class="absolute top-6 left-6 flex items-center gap-3">
        <div 
          class="w-3 h-3 rounded-full"
          :class="wsConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'"
        ></div>
        <span class="text-white/50 text-sm font-mono">
          {{ wsConnected ? 'CONNECTÉ' : 'DÉCONNECTÉ' }}
        </span>
      </div>

      <!-- Progress indicator -->
      <div class="absolute top-6 right-6 text-white/50 text-sm font-mono">
        Position: {{ localPosition }} / {{ partition.length }}
      </div>

      <!-- START INSTRUCTION: Only at the very beginning (position 0 and not started) -->
      <div v-if="riftReady && isDreamTurn && !gameStarted" class="flex flex-col items-center gap-8">
        <h2 class="text-white/70 text-2xl font-light tracking-widest uppercase">
          PRÊT À COMMENCER ?
        </h2>
        
        <!-- Instruction animation -->
        <div class="relative w-64 h-64 flex items-center justify-center">
          <!-- Pulsing sphero icon -->
          <div class="text-8xl animate-bounce">🔮</div>
          <div class="absolute inset-0 bg-[#ff1493]/20 rounded-full blur-3xl -z-10 animate-pulse"></div>
        </div>

        <div class="text-[#ff1493] text-3xl font-bold tracking-wider text-center">
          SECOUE UN SPHERO
        </div>
        
        <div class="text-white/50 text-lg text-center">
          pour lancer la partition
        </div>
      </div>

      <!-- DREAM Content: Show note to play -->
      <div v-else-if="riftReady && isDreamTurn && gameStarted" class="flex flex-col items-center gap-8">
        <h2 class="text-white/70 text-2xl font-light tracking-widest uppercase">
          JOUE CETTE NOTE
        </h2>
        
        <!-- Note Image -->
        <div class="relative">
          <transition name="note-pop" mode="out-in">
            <img 
              :key="currentNote + '-' + currentPosition"
              :src="getNoteImage(currentNote)"
              class="w-64 h-64 object-contain drop-shadow-2xl"
              :alt="`Note ${currentNote}`"
            />
          </transition>
          
          <!-- Glow effect -->
          <div class="absolute inset-0 bg-[#ff1493]/20 rounded-full blur-3xl -z-10 animate-pulse"></div>
        </div>

        <!-- Note name -->
        <div class="text-[#ff1493] text-4xl font-bold tracking-wider">
          {{ getNoteName(currentNote) }}
        </div>

        <!-- Sphero indicator -->
        <div class="text-white/50 text-lg">
          🔮 Secoue le Sphero {{ getSpheroName(currentNote) }}
        </div>
      </div>

      <!-- NIGHTMARE Content: Show waiting message -->
      <div v-else-if="riftReady && isNightmareTurn" class="flex flex-col items-center gap-8">
        <div class="text-white/30 text-xl font-light tracking-widest uppercase">
          En attente...
        </div>
        
        <!-- Waiting animation -->
        <div class="relative w-48 h-48 flex items-center justify-center">
          <div class="absolute inset-0 border-4 border-white/10 rounded-full"></div>
          <div class="absolute inset-4 border-4 border-white/20 rounded-full animate-spin-slow"></div>
          <div class="absolute inset-8 border-4 border-white/10 rounded-full animate-spin-reverse"></div>
          
          <!-- Center icon -->
          <div class="text-6xl opacity-50">🌙</div>
        </div>

        <div class="text-white/40 text-lg">
          C'est au tour du Nightmare
        </div>
        
        <div class="text-white/20 text-sm">
          Prépare-toi pour ta prochaine note...
        </div>
      </div>

      <!-- IDLE: Waiting to start -->
      <div v-else class="flex flex-col items-center gap-8">
        <div class="text-white/50 text-xl font-light tracking-widest uppercase">
          En attente de la partie...
        </div>
        
        <div class="w-16 h-16 border-4 border-white/20 border-t-[#ff1493] rounded-full animate-spin"></div>
      </div>

      <!-- COMPLETED -->
      <div v-if="isCompleted" class="absolute inset-0 flex items-center justify-center bg-black/80 z-20">
        <div class="flex flex-col items-center gap-6">
          <div class="text-6xl">🎉</div>
          <div class="text-[#ff1493] text-4xl font-bold tracking-wider">
            PARTITION TERMINÉE !
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';

// No layout for fullscreen experience
definePageMeta({ layout: false });

// WebSocket state
const ws = ref(null);
const wsConnected = ref(false);
const state = ref({
  depth_current_player: 'dream',
  depth_partition: [1, 2, 3, 4, 5, 6, 5, 4, 5, 1, 3, 2, 2, 3, 1, 2, 5, 6, 4, 5],
  depth_partition_position: 0
});

// Game started state (once started, shows notes directly)
const gameStarted = ref(false);

// Track last position to detect changes
const lastPosition = ref(-1);

// Local position tracking (since server doesn't always send position updates)
const localPosition = ref(0);

// Game state from server
const partition = computed(() => state.value.depth_partition || []);
const currentPosition = computed(() => state.value.depth_partition_position || 0);
const currentPlayer = computed(() => state.value.depth_current_player || null);

// Current note to play (based on LOCAL position for real-time updates)
const currentNote = computed(() => {
  if (localPosition.value >= partition.value.length) return null;
  return partition.value[localPosition.value];
});

// Is rift ready? (rift_part_count == 2)
const riftReady = computed(() => state.value.rift_part_count === 2);

// Is it Dream's turn? (notes 1-3)
const isDreamTurn = computed(() => {
  if (!currentNote.value) return false;
  return currentNote.value >= 1 && currentNote.value <= 3;
});

// Is it Nightmare's turn? (notes 4-6)
const isNightmareTurn = computed(() => {
  if (!currentNote.value) return false;
  return currentNote.value >= 4 && currentNote.value <= 6;
});

// Is partition completed?
const isCompleted = computed(() => {
  return partition.value.length > 0 && localPosition.value >= partition.value.length;
});

// Watch for position changes - when position changes, the game has progressed
watch(currentPosition, (newPos, oldPos) => {
  if (newPos !== oldPos && newPos > 0) {
    // Position advanced, game has started and is progressing
    lastPosition.value = newPos;
  }
});

// Note images (1, 2, 3 for Dream)
function getNoteImage(note) {
  const noteImages = {
    1: '/depth-diapo/DO.png',
    2: '/depth-diapo/RE.png',
    3: '/depth-diapo/MI.png',
  };
  return noteImages[note] || '/depth-diapo/DO.png';
}

// Note names
function getNoteName(note) {
  const names = { 1: 'DO', 2: 'RE', 3: 'MI' };
  return names[note] || '?';
}

// Reverse lookup: note name to note number
function getNoteNumber(noteName) {
  const map = { 'DO': 1, 'RE': 2, 'MI': 3 };
  return map[noteName] || null;
}

// Sphero names
function getSpheroName(note) {
  const spheros = { 
    1: 'SB-08C9',
    2: 'SB-1219', 
    3: 'SB-2020'
  };
  return spheros[note] || '?';
}

// WebSocket connection
function connectWebSocket() {
  const wsUrl = 'ws://192.168.10.7:8000/ws';
  
  try {
    ws.value = new WebSocket(wsUrl);
    
    ws.value.onopen = () => {
      console.log('WebSocket connected');
      wsConnected.value = true;
    };
    
    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Message received:', data);
        
        // Check if this is a game start signal
        if (data.depth_game_started) {
          console.log('🎮 Game started signal received!');
          gameStarted.value = true;
        }
        
        // Check if this is a depth_note message (correct note played)
        if (data.depth_note && gameStarted.value) {
          const playedNote = getNoteNumber(data.depth_note);
          const expectedNote = currentNote.value;
          
          console.log(`🔮 Note received: ${data.depth_note} (${playedNote}), expected: ${expectedNote}`);
          
          // If this note matches current expected note, advance to next
          if (playedNote === expectedNote) {
            console.log('✅ Correct note! Advancing to next...');
            localPosition.value++;
            console.log(`📍 New position: ${localPosition.value}`);
          }
        }
        
        // Check for depth_sound "false" = wrong note, RETRY (back to first note, not start instruction)
        if (data.depth_sound === 'false') {
          console.log('❌ Wrong note! RETRY - Back to first note...');
          localPosition.value = 0;
          // Keep gameStarted = true, so we stay on notes (not shake instruction)
        }
        
        // Update state - merge all non-null values
        for (const [key, value] of Object.entries(data)) {
          if (value !== null && value !== undefined) {
            state.value[key] = value;
          }
        }
        console.log('📊 State after merge:', JSON.stringify(state.value));
        
        // Sync local position with server position
        if (data.depth_partition_position !== undefined && data.depth_partition_position !== null) {
          localPosition.value = data.depth_partition_position;
          
          // If position > 0, game is already in progress
          if (data.depth_partition_position > 0) {
            gameStarted.value = true;
          }
        }
        
        // Reset position if it goes back to 0 (RETRY) - but keep gameStarted = true to show first note
        if (data.depth_partition_position === 0 && lastPosition.value > 0) {
          console.log('🔄 RETRY detected - back to first note');
          // Keep gameStarted = true so we stay on the notes display, not the "shake to start" screen
          localPosition.value = 0;
        }
        lastPosition.value = data.depth_partition_position ?? lastPosition.value;
        
      } catch (e) {
        console.error('Failed to parse message:', e);
      }
    };
    
    ws.value.onclose = () => {
      console.log('WebSocket closed, reconnecting...');
      wsConnected.value = false;
      setTimeout(connectWebSocket, 3000);
    };
    
    ws.value.onerror = (error) => {
      console.error('WebSocket error:', error);
      wsConnected.value = false;
    };
  } catch (e) {
    console.error('Failed to connect:', e);
    setTimeout(connectWebSocket, 3000);
  }
}

onMounted(() => {
  connectWebSocket();
});

onUnmounted(() => {
  if (ws.value) {
    ws.value.close();
  }
});
</script>

<style scoped>
/* Slow spin */
@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin-slow {
  animation: spin-slow 8s linear infinite;
}

/* Reverse spin */
@keyframes spin-reverse {
  from { transform: rotate(360deg); }
  to { transform: rotate(0deg); }
}

.animate-spin-reverse {
  animation: spin-reverse 12s linear infinite;
}

/* Note pop transition */
.note-pop-enter-active {
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.note-pop-leave-active {
  transition: all 0.2s ease-out;
}

.note-pop-enter-from {
  opacity: 0;
  transform: scale(0.5) rotate(-10deg);
}

.note-pop-leave-to {
  opacity: 0;
  transform: scale(1.2) rotate(10deg);
}
</style>
