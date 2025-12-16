<template>
  <div class="min-h-screen bg-bg-main text-text-main p-10 flex justify-center selection:bg-accent selection:text-accent-text">
    <div class="w-full max-w-4xl">
      <!-- Top Bar -->
      <div class="flex justify-between items-center mb-8 border-b border-border pb-4">
        <div>
          <h1 class="text-2xl font-bold uppercase tracking-widest text-accent mb-1">Led Controller</h1>
          <h2 class="text-xs uppercase tracking-wider text-text-sec">Animation Studio</h2>
        </div>
        <div class="flex gap-2">
          <select v-model="selectedPreset" @change="loadPreset" class="raw-input w-40 h-10 uppercase text-xs">
            <option value="">Load Preset...</option>
            <option value="police">Police Lights</option>
            <option value="rainbow">Rainbow Wave</option>
            <option value="pulse">Blue Pulse</option>
          </select>
          <button @click="showJson = !showJson" class="tri-state-btn px-4 h-10 border border-border bg-bg-sec hover:bg-bg-main hover:border-border-focus uppercase text-xs font-bold transition-all">
            Toggle JSON
          </button>
        </div>
      </div>

      <!-- Preview -->
      <div class="section-box mb-8 bg-bg-sec/50">
        <div class="section-title">Live Preview</div>
        <div class="flex justify-between items-center mb-4">
          <span class="text-xs font-bold uppercase text-text-sec">Status: <span :class="isPlaying ? 'text-success' : 'text-text-sec'">{{ isPlaying ? 'PLAYING' : 'STOPPED' }}</span></span>
          <div class="flex gap-2">
            <button 
              @click="playPreview" 
              v-if="!isPlaying"
              class="h-8 px-4 bg-accent text-accent-text uppercase text-xs font-bold hover:opacity-90 active:scale-95 transition-all"
            >
              ▶ Play
            </button>
            <button 
              @click="stopPreview" 
              v-else
              class="h-8 px-4 border border-red-500 text-red-500 hover:bg-red-500/10 uppercase text-xs font-bold transition-all"
            >
              ■ Stop
            </button>
          </div>
        </div>
        <div class="h-10 w-full bg-black rounded-sm flex overflow-hidden shadow-inner border border-border">
          <div
            v-for="(color, i) in previewPixels"
            :key="i"
            class="flex-1 h-full"
            :style="{ backgroundColor: color }"
          ></div>
        </div>
      </div>

      <!-- Frames List -->
      <div class="flex flex-col gap-4">
        <div v-for="(frame, index) in animation.frames" :key="index" class="relative border border-border bg-bg-sec p-4 hover:border-border-focus transition-colors">
          <div class="flex justify-between items-center mb-4 border-b border-border border-dashed pb-2">
            <span class="text-sm font-bold uppercase text-text-sec">Frame {{ index + 1 }}</span>
            <div class="flex items-center gap-2">
              <span class="text-xs uppercase text-text-sec">Time (ms):</span>
              <input type="number" v-model.number="frame.time" class="raw-input w-20 text-center" />
              <button 
                @click="removeFrame(index)"
                class="ml-2 text-xs text-red-500 hover:text-red-400 uppercase font-bold px-2 py-1 hover:bg-red-500/10 rounded transition-colors"
              >
                Remove
              </button>
            </div>
          </div>

          <div class="px-2">
            <div
              class="h-8 relative rounded cursor-crosshair shadow-inner border border-border/50"
              :style="{ background: getGradientStyle(frame) }"
              @click="addStop(index, $event)"
              @mousemove="onTrackMouseMove"
              ref="trackRefs"
            >
              <div
                v-for="(color, cIndex) in frame.colors"
                :key="cIndex"
                class="absolute -top-1 w-3 h-10 bg-white border-2 border-black rounded cursor-grab shadow-lg hover:scale-110 active:cursor-grabbing transition-transform z-10"
                :style="{ left: color.position + '%', background: `rgb(${color.color})`, transform: 'translateX(-50%)' }"
                @mousedown.stop="startDrag(index, cIndex, $event)"
                @contextmenu.prevent.stop="removeStop(index, cIndex)"
                @click.stop
              ></div>
            </div>
          </div>
          <div class="mt-2 text-right text-[10px] uppercase text-text-sec tracking-wider">
            L-Click add • Drag move • R-Click remove • Click color
          </div>
        </div>
      </div>

      <div class="mt-6 text-center">
        <button 
          @click="addFrame" 
          class="w-full py-4 border-2 border-dashed border-border text-text-sec hover:text-accent hover:border-accent uppercase font-bold tracking-widest transition-all bg-transparent hover:bg-bg-sec"
        >
          + Add Frame
        </button>
      </div>

      <textarea
        v-if="showJson"
        readonly
        class="code-preview w-full h-40 mt-6 rounded-none outline-none resize-y"
        :value="JSON.stringify(animation, null, 4)"
      ></textarea>
      
      <!-- hidden color input for picker -->
      <input 
        type="color" 
        ref="colorPicker" 
        style="display:none" 
        @input="onColorPicked"
      >
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';

// --- DATA ---
const NUM_PIXELS = 30;
const animation = reactive({
  name: 'My Animation',
  frames: [
    {
      time: 500,
      colors: [
        { color: '255,0,0', position: 0 },
        { color: '0,0,255', position: 100 },
      ],
    },
  ],
});

const showJson = ref(false);
const selectedPreset = ref('');
const trackRefs = ref([]);
const colorPicker = ref(null);

// Preview State
const isPlaying = ref(false);
const previewPixels = ref(Array(NUM_PIXELS).fill('rgb(0,0,0)'));
let playIntervalId = null;

// Drag State
const dragState = reactive({
  active: false,
  frameIndex: -1,
  colorIndex: -1,
  startX: 0,
  hasMoved: false,
  trackRect: null,
});

// Color Picker State
const pickerState = reactive({
  frameIndex: -1,
  colorIndex: -1,
});

// --- METHODS ---

// Presets
const PRESETS = {
  police: {
    frames: [
      { time: 150, colors: [{ color: "255,0,0", position: 0 }, { color: "255,0,0", position: 45 }, { color: "0,0,0", position: 50 }, { color: "0,0,255", position: 55 }, { color: "0,0,255", position: 100 }] },
      { time: 150, colors: [{ color: "0,0,255", position: 0 }, { color: "0,0,255", position: 45 }, { color: "0,0,0", position: 50 }, { color: "255,0,0", position: 55 }, { color: "255,0,0", position: 100 }] }
    ]
  },
  pulse: {
    frames: [
      { time: 1000, colors: [{ color: "0,0,0", position: 0 }, { color: "0,0,255", position: 50 }, { color: "0,0,0", position: 100 }] },
      { time: 1000, colors: [{ color: "0,0,50", position: 0 }, { color: "0,0,100", position: 50 }, { color: "0,0,50", position: 100 }] }
    ]
  },
  rainbow: {
    frames: [
      { time: 2000, colors: [{ color: "255,0,0", position: 0 }, { color: "0,255,0", position: 33 }, { color: "0,0,255", position: 66 }, { color: "255,0,0", position: 100 }] },
      { time: 2000, colors: [{ color: "0,0,255", position: 0 }, { color: "255,0,0", position: 33 }, { color: "0,255,0", position: 66 }, { color: "0,0,255", position: 100 }] }
    ]
  }
};

function loadPreset() {
  if (PRESETS[selectedPreset.value]) {
    // Deep clone
    animation.frames = JSON.parse(JSON.stringify(PRESETS[selectedPreset.value].frames));
  }
}

// Frame Management
function addFrame() {
  animation.frames.push({
    time: 500,
    colors: [
      { color: '0,0,0', position: 0 },
      { color: '0,0,0', position: 100 },
    ],
  });
}

function removeFrame(index) {
  if (animation.frames.length > 1) {
    animation.frames.splice(index, 1);
  }
}

// Gradient Logic
function getGradientStyle(frame) {
  const sorted = [...frame.colors].sort((a, b) => a.position - b.position);
  const stops = sorted.map((c) => `rgb(${c.color}) ${c.position}%`).join(', ');
  return `linear-gradient(to right, ${stops})`;
}

function addStop(frameIndex, event) {
  // Check if we just finished a drag or click on handle handled by stopPropagation
  if (dragState.active) return;
  
  const rect = event.target.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const pct = Math.max(0, Math.min(100, Math.round((x / rect.width) * 100)));
  
  animation.frames[frameIndex].colors.push({
    color: '255,255,255',
    position: pct,
  });
}

function removeStop(frameIndex, colorIndex) {
  if (animation.frames[frameIndex].colors.length > 1) {
    animation.frames[frameIndex].colors.splice(colorIndex, 1);
  }
}

// Dragging
function startDrag(frameIndex, colorIndex, event) {
  const track = event.target.parentElement;
  dragState.active = true;
  dragState.frameIndex = frameIndex;
  dragState.colorIndex = colorIndex;
  dragState.startX = event.clientX;
  dragState.hasMoved = false;
  dragState.trackRect = track.getBoundingClientRect();
  
  window.addEventListener('mousemove', onGlobalMouseMove);
  window.addEventListener('mouseup', onGlobalMouseUp);
}

function onGlobalMouseMove(e) {
  if (!dragState.active) return;
  
  if (!dragState.hasMoved && Math.abs(e.clientX - dragState.startX) > 3) {
    dragState.hasMoved = true;
  }
  
  if (dragState.hasMoved) {
    const dx = e.clientX - dragState.trackRect.left;
    let pct = (dx / dragState.trackRect.width) * 100;
    pct = Math.max(0, Math.min(100, Math.round(pct)));
    
    // Update model
    if (animation.frames[dragState.frameIndex] && animation.frames[dragState.frameIndex].colors[dragState.colorIndex]) {
        animation.frames[dragState.frameIndex].colors[dragState.colorIndex].position = pct;
    }
  }
}

function onGlobalMouseUp(e) {
  if (dragState.active) {
    if (!dragState.hasMoved) {
      // It was a click, open color picker
      openColorPicker(dragState.frameIndex, dragState.colorIndex);
    }
    dragState.active = false;
    dragState.trackRect = null;
    window.removeEventListener('mousemove', onGlobalMouseMove);
    window.removeEventListener('mouseup', onGlobalMouseUp);
  }
}

// Ensure event listener removal
onUnmounted(() => {
    window.removeEventListener('mousemove', onGlobalMouseMove);
    window.removeEventListener('mouseup', onGlobalMouseUp);
});

// Color Picker
function openColorPicker(fIdx, cIdx) {
  pickerState.frameIndex = fIdx;
  pickerState.colorIndex = cIdx;
  
  const colorStr = animation.frames[fIdx].colors[cIdx].color; // "r,g,b"
  const rgb = colorStr.split(',').map(Number);
  
  // Convert rgb to hex for input
  const hex = "#" + ((1 << 24) + (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]).toString(16).slice(1);
  colorPicker.value.value = hex;
  colorPicker.value.click();
}

function onColorPicked(e) {
    const hex = e.target.value;
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    
    if (pickerState.frameIndex >= 0) {
        animation.frames[pickerState.frameIndex].colors[pickerState.colorIndex].color = `${r},${g},${b}`;
    }
}


// --- PREVIEW PLAYER ---
function calculateFramePixels(frame) {
    const stops = frame.colors.map(c => ({
        pos: c.position,
        rgb: c.color.split(',').map(Number)
    })).sort((a, b) => a.pos - b.pos);
    
    const pixels = [];
    for (let i = 0; i < NUM_PIXELS; i++) {
        const pct = (i / (NUM_PIXELS - 1)) * 100;
        let start = stops[0], end = stops[stops.length - 1];

        if (pct <= start.pos) { start = start; end = start; }
        else if (pct >= end.pos) { start = end; end = end; }
        else {
            for (let j = 0; j < stops.length - 1; j++) {
                if (pct >= stops[j].pos && pct <= stops[j + 1].pos) {
                    start = stops[j]; end = stops[j + 1]; break;
                }
            }
        }

        const range = end.pos - start.pos;
        const ratio = range === 0 ? 0 : (pct - start.pos) / range;

        const r = Math.round(start.rgb[0] + (end.rgb[0] - start.rgb[0]) * ratio);
        const g = Math.round(start.rgb[1] + (end.rgb[1] - start.rgb[1]) * ratio);
        const b = Math.round(start.rgb[2] + (end.rgb[2] - start.rgb[2]) * ratio);
        
        pixels.push(`rgb(${r},${g},${b})`);
    }
    return pixels;
}

async function playPreview() {
    if (isPlaying.value) return;
    isPlaying.value = true;
    
    const loop = async () => {
        for (const frame of animation.frames) {
             if (!isPlaying.value) break;
             previewPixels.value = calculateFramePixels(frame);
             await new Promise(r => setTimeout(r, frame.time));
        }
        if (isPlaying.value) loop();
    };
    loop();
}

function stopPreview() {
    isPlaying.value = false;
}

</script>

<style scoped>
/* Custom utility-like classes that mirror clients.html but use Tailwind @apply in main.css or here */
.raw-input {
  @apply border border-border bg-bg-sec text-text-main px-3 py-2 text-xs w-full outline-none transition-all focus:border-border-focus focus:bg-bg-main;
}

.section-box {
  @apply border border-border p-6 relative;
}

.section-title {
  @apply absolute -top-3 left-4 bg-bg-main px-2 font-bold uppercase text-xs tracking-wider text-text-main transition-colors duration-300;
}

.code-preview {
  @apply font-mono text-[11px] bg-[var(--code-bg)] text-text-main p-4 border border-border whitespace-pre-wrap;
  background-color: #1a1a1a; /* Fallback/Specific override if needed */
}
</style>
