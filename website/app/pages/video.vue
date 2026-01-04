<template>
  <div 
    class="fixed inset-0 bg-black flex items-center justify-center overflow-hidden font-mono select-none"
    @mousemove="onUserActivity"
    @click="onUserActivity"
  >
    <!-- Main Video Player -->
    <video
      v-show="currentVideo && !videoError"
      ref="videoRef"
      class="w-full h-full object-cover"
      :src="currentVideo"
      autoplay
      loop
      muted
      playsinline
      @error="handleVideoError"
      @loadeddata="onVideoLoaded"
      @timeupdate="onTimeUpdate"
      @ended="isPlaying = false"
      @play="isPlaying = true"
      @pause="isPlaying = false"
    ></video>

    <!-- UI Overlay (Fades out when inactive) -->
    <div 
        class="absolute inset-0 pointer-events-none transition-opacity duration-500 flex flex-col justify-between p-8"
        :class="uiVisible ? 'opacity-100' : 'opacity-0'"
    >
        <!-- Header: Filename -->
        <div class="pointer-events-auto flex justify-between items-start">
            <div class="bg-black/50 backdrop-blur-md px-4 py-2 rounded border border-white/10 text-white/80 text-sm font-bold tracking-wider">
                <span class="text-[#33ff00] mr-2">●</span> {{ currentVideo || 'IDLE' }}
            </div>
            
             <!-- Connection Status -->
            <div class="bg-black/50 backdrop-blur-md px-4 py-2 rounded border border-white/10 flex items-center gap-3">
                <div 
                    class="w-2 h-2 rounded-full transition-colors duration-500"
                    :class="isConnected ? 'bg-[#33ff00] shadow-[0_0_10px_#33ff00]' : 'bg-red-500 animate-pulse'"
                ></div>
                <span class="text-[10px] tracking-wider uppercase opacity-50 text-white">
                    {{ isConnected ? 'ONLINE' : 'OFFLINE' }}
                </span>
            </div>
        </div>

        <!-- Center: Navigation Arrows -->
        <div class="pointer-events-auto flex justify-between items-center w-full px-4">
            <button 
                @click="prevVideo"
                class="group p-4 hover:bg-white/10 rounded-full transition-all active:scale-95"
            >
                <div class="text-white/50 group-hover:text-[#33ff00] transition-colors text-4xl font-black">
                    &lt;
                </div>
            </button>
            
            <button 
                @click="nextVideo"
                class="group p-4 hover:bg-white/10 rounded-full transition-all active:scale-95"
            >
                <div class="text-white/50 group-hover:text-[#33ff00] transition-colors text-4xl font-black">
                    &gt;
                </div>
            </button>
        </div>

        <!-- Bottom: Controls -->
        <div class="pointer-events-auto bg-black/50 backdrop-blur-md p-4 rounded border border-white/10 space-y-2">
            <!-- Progress Bar -->
            <div 
                class="w-full h-1 bg-white/20 rounded cursor-pointer relative group"
                @click="seek"
            >
                <div 
                    class="absolute top-0 left-0 h-full bg-[#33ff00] shadow-[0_0_10px_#33ff00]" 
                    :style="{ width: `${progress}%` }"
                ></div>
                <div class="absolute inset-0 hover:bg-white/10 transition-colors"></div>
            </div>
            
            <div class="flex justify-between items-center text-xs text-white/70 uppercase tracking-widest">
                 <button 
                    @click="togglePlay" 
                    class="hover:text-white hover:scale-105 transition-all w-8 font-bold"
                 >
                    {{ isPlaying ? 'PAUSE' : 'PLAY' }}
                 </button>
                 <span>{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</span>
            </div>
        </div>
    </div>

    <!-- Fallback / No Signal UI -->
    <div v-if="!currentVideo || videoError" class="absolute inset-0 z-10 flex flex-col items-center justify-center bg-[#0a0a0a] text-[#33ff00]">
      <div class="grid place-items-center gap-6">
        <div class="relative w-32 h-32 border-4 border-[#33ff00]/30 rounded-full animate-pulse flex items-center justify-center">
             <div class="w-24 h-24 border-2 border-[#33ff00]/60 rounded-full"></div>
             <div class="absolute w-full h-[2px] bg-[#33ff00] animate-[scan_2s_ease-in-out_infinite] opacity-50"></div>
        </div>

        <div class="text-center space-y-2">
            <h1 class="text-4xl font-black tracking-[0.2em] glitch-text">
                {{ videoError ? 'SIGNAL LOST' : 'SYSTEM IDLE' }}
            </h1>
            <p class="text-sm tracking-widest opacity-70 uppercase">
                {{ videoError ? 'FEED INTERRUPTED' : 'AWAITING PROTOCOL' }}
            </p>
            <p v-if="videoError" class="text-xs text-red-500 mt-4 bg-red-500/10 px-4 py-2 rounded border border-red-500/20">
                FILE NOT FOUND: {{ currentVideo }}
            </p>
            <p v-else class="text-xs text-[#33ff00] mt-4 bg-[#33ff00]/10 px-4 py-2 rounded border border-[#33ff00]/20 animate-pulse">
                LISTENING ON PORT 81
            </p>
        </div>
        
        <div class="absolute bottom-10 text-[10px] opacity-40 tracking-[0.5em] animate-pulse">
            {{ videoError ? 'RETRYING_CONNECTION...' : 'READY_TO_LAUNCH' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue';

const VIDEO_LIST = ['/video1.mp4', '/video2.mp4'];

// Use Shared Composable
// Assumed auto-import or available globally in Nuxt context
const { isConnected, lastPayload, connect } = useRiftSocket();

// State
const currentVideo = ref(null); // Start in IDLE state 
const videoError = ref(false);
const videoRef = ref(null);
const uiVisible = ref(true);
const isPlaying = ref(false);
const progress = ref(0);
const currentTime = ref(0);
const duration = ref(0);

let uiTimeout = null;

// --- Watchers ---

// Watch global payload for video commands
watch(lastPayload, (newPayload) => {
    if (newPayload?.lost_video_play) {
        console.log(`[Video] Received command: ${newPayload.lost_video_play}`);
        const filename = newPayload.lost_video_play.startsWith('/') ? newPayload.lost_video_play : `/${newPayload.lost_video_play}`;
        changeVideo(filename);
    }
}, { deep: true });

// Reset error when source changes
watch(currentVideo, () => {
    videoError.value = false;
});

// --- UI Logic ---
function onUserActivity() {
    uiVisible.value = true;
    if (uiTimeout) clearTimeout(uiTimeout);
    uiTimeout = setTimeout(() => {
        uiVisible.value = false;
    }, 3000); // Hide after 3s of inactivity
}

function togglePlay() {
    if (!videoRef.value) return;
    if (videoRef.value.paused) videoRef.value.play();
    else videoRef.value.pause();
}

function nextVideo() {
    const idx = VIDEO_LIST.indexOf(currentVideo.value);
    const nextIdx = (idx + 1) % VIDEO_LIST.length;
    changeVideo(VIDEO_LIST[nextIdx]);
}

function prevVideo() {
    const idx = VIDEO_LIST.indexOf(currentVideo.value);
    const prevIdx = (idx - 1 + VIDEO_LIST.length) % VIDEO_LIST.length;
    changeVideo(VIDEO_LIST[prevIdx]);
}

function changeVideo(path) {
    if (!VIDEO_LIST.includes(path)) VIDEO_LIST.push(path);
    currentVideo.value = path;
}

function seek(e) {
    if (!videoRef.value) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const pct = (e.clientX - rect.left) / rect.width;
    videoRef.value.currentTime = pct * videoRef.value.duration;
}

function onTimeUpdate() {
    if (!videoRef.value) return;
    currentTime.value = videoRef.value.currentTime;
    progress.value = (videoRef.value.currentTime / videoRef.value.duration) * 100 || 0;
}

function onVideoLoaded() {
    videoError.value = false;
    if (videoRef.value) duration.value = videoRef.value.duration;
}

function formatTime(s) {
    const mins = Math.floor(s / 60);
    const secs = Math.floor(s % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function handleVideoError(e) {
    console.warn(`[Video] Failed to load source: ${currentVideo.value}`, e);
    videoError.value = true;
}

onMounted(() => {
  connect(); // Ensure socket is active
  onUserActivity();
});

onUnmounted(() => {
  if (uiTimeout) clearTimeout(uiTimeout);
  // We don't disconnect socket here as it might be used by other components now
});
</script>

<style scoped>
/* Glitch Text Effect */
.glitch-text {
  text-shadow: 2px 0 #ff0000, -2px 0 #0000ff;
  animation: glitch 1s infinite alternate-reverse;
}

@keyframes glitch {
  0% { text-shadow: 2px 0 #ff0000, -2px 0 #0000ff; transform: skewX(0deg); }
  20% { text-shadow: -2px 0 #ff0000, 2px 0 #0000ff; transform: skewX(10deg); }
  40% { text-shadow: 2px 0 #ff0000, -2px 0 #0000ff; transform: skewX(-5deg); }
  60% { text-shadow: -2px 0 #ff0000, 2px 0 #0000ff; transform: skewX(0deg); opacity: 1; }
  80% { opacity: 0.8; }
  100% { transform: skewX(0deg); }
}

@keyframes scan {
    0% { top: 0%; opacity: 0; }
    50% { opacity: 1; }
    100% { top: 100%; opacity: 0; }
}
</style>
