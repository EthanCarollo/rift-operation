<template>
  <div class="absolute inset-0 z-20 pointer-events-none">
    <audio ref="musicRef" :src="currentMusic" :loop="shouldLoop" autoplay muted @loadeddata="onMusicLoaded"
      @error="handleMusicError"></audio>
    <audio ref="sfxRef" @error="handleSfxError"></audio>
    <!-- TOP LEFT: Connection Status -->
    <div
      class="absolute top-6 left-6 flex items-center gap-3 bg-black/40 backdrop-blur px-3 py-1.5 rounded-full border border-white/10 pointer-events-auto">
      <div class="w-2 h-2 rounded-full transition-colors duration-500"
        :class="isConnected ? 'bg-[#33ff00] shadow-[0_0_8px_#33ff00]' : 'bg-red-500 animate-pulse'"></div>
      <span class="text-[10px] font-bold tracking-wider uppercase text-white/80">
        {{ isConnected ? 'ONLINE' : 'OFFLINE' }}
      </span>
    </div>
    <!-- TOP RIGHT: Debug Panel -->
    <div v-if="showDebug"
      class="absolute top-6 right-6 bg-black/60 p-3 rounded border border-white/10 text-[10px] text-white/50 font-mono leading-tight z-50 pointer-events-auto">
      <div>STATE: <span class="text-white">{{ state }}</span></div>
      <div class="mt-1 text-purple-400">VIDEO: {{ videoName }}</div>
      <div class="text-green-400">MUSIC: {{ currentMusic?.split('/').pop() || 'None' }}</div>
      <!-- DEV CONTROLS -->
      <div class="mt-2 pt-2 border-t border-white/10 flex flex-col gap-1">
        <button @click="$emit('simulate')"
          class="px-2 py-1 bg-blue-500/20 text-blue-300 hover:bg-blue-500/40 rounded text-center">
          Simulate Recon
        </button>
        <button @click="$emit('capture')"
          class="px-2 py-1 bg-purple-500/20 text-purple-300 hover:bg-purple-500/40 rounded text-center">
          Simulate Capture
        </button>
      </div>
    </div>
    <!-- TOP CENTER: Health Bar -->
    <div class="absolute top-[20%] left-0 right-0 flex justify-center">
      <div class="w-[60vw] max-w-2xl">
        <div class="flex justify-between text-xs uppercase tracking-widest text-white/60 mb-2 px-1">
          <span>Santé de l'Étranger</span>
          <span>{{ hp * 20 }}%</span>
        </div>
        <div class="flex gap-1 h-3">
          <div v-for="i in 5" :key="i" class="flex-1 rounded-sm transition-all duration-500"
            :class="i <= hp ? 'bg-gradient-to-r from-red-500 to-red-600 shadow-[0_0_12px_rgba(220,38,38,0.6)]' : 'bg-white/10'">
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
defineProps({
  isConnected: Boolean,
  showDebug: Boolean,
  state: String,
  hp: Number,
  attack: String,
  videoName: String,
  currentMusic: String,
  shouldLoop: Boolean
});
defineEmits(['simulate', 'capture']);

const musicRef = ref(null);
const sfxRef = ref(null);

function handleMusicError(e) {
  console.warn('[Battle] Failed to load music:', e);
}

function handleSfxError(e) {
  console.warn('[Battle] Failed to load SFX:', e);
}

function onMusicLoaded() {
  // Once music is loaded, unmute it (autoplay works when muted)
  if (musicRef.value && musicRef.value.muted) {
    console.log('[HUD] Music loaded, unmuting...');
    musicRef.value.muted = false;
    musicRef.value.volume = 1.0;
  }
}

// Expose music and SFX control for parent
defineExpose({
  playMusic() {
    if (musicRef.value) {
      console.log('[HUD] playMusic called, src:', musicRef.value.src, 'loop:', musicRef.value.loop);
      musicRef.value.muted = false; // Ensure unmuted
      musicRef.value.volume = 1.0; // Full volume
      musicRef.value.play()
        .then(() => console.log('[HUD] Music playing successfully'))
        .catch(e => console.log('[Music] Play failed:', e.message));
    } else {
      console.warn('[HUD] playMusic called but musicRef is null');
    }
  },
  pauseMusic() {
    if (musicRef.value) {
      musicRef.value.pause();
    }
  },
  lowerMusicVolume() {
    if (musicRef.value) {
      musicRef.value.volume = 0.3; // Lower to 30% for SFX
    }
  },
  restoreMusicVolume() {
    if (musicRef.value) {
      musicRef.value.volume = 1.0; // Restore to 100%
    }
  },
  playSFX(src) {
    if (sfxRef.value) {
      sfxRef.value.src = src;
      sfxRef.value.loop = false; // SFX don't loop
      sfxRef.value.volume = 1.0;
      sfxRef.value.play().catch(e => console.log('[SFX] Play failed:', e));
    }
  }
});
</script>
