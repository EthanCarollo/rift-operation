<template>
  <div class="min-h-screen bg-bg-main text-text-main p-10 flex justify-center selection:bg-accent selection:text-accent-text">
    <div class="w-full max-w-4xl">
      <!-- Top Bar -->
      <div class="flex justify-between items-center mb-8 border-b border-border pb-4">
        <div>
          <h1 class="text-2xl font-bold uppercase tracking-widest text-accent mb-1">Led Controller</h1>
          <h2 class="text-xs uppercase tracking-wider text-text-sec">Animation Studio</h2>
        </div>
        <div class="flex gap-4 items-center">

          <div class="flex gap-2">
           <select v-model="selectedPreset" @change="loadPreset" class="raw-input w-40 h-10 uppercase text-xs">
            <option value="">Load Preset...</option>
            <option value="police">Police Lights</option>
            <option value="rainbow">Rainbow Wave</option>
            <option value="pulse">Blue Pulse</option>
          </select>
          <button @click="importJson" class="tri-state-btn px-4 h-10 border border-border bg-bg-sec hover:bg-bg-main hover:border-border-focus uppercase text-xs font-bold transition-all">
            Import
          </button>
          <button @click="downloadJson" class="tri-state-btn px-4 h-10 border border-accent bg-accent/10 text-accent hover:bg-accent hover:text-accent-text uppercase text-xs font-bold transition-all">
            Download
          </button>
          <button @click="copyJson" class="tri-state-btn px-4 h-10 border border-border bg-bg-sec hover:bg-bg-main hover:border-border-focus uppercase text-xs font-bold transition-all">
            {{ copyFeedback || 'Copy' }}
          </button>
          <button @click="showJson = !showJson" class="tri-state-btn px-4 h-10 border border-border bg-bg-sec hover:bg-bg-main hover:border-border-focus uppercase text-xs font-bold transition-all">
            JSON
          </button>
          </div>
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
                :style="{ left: color.position + '%', background: getPreviewColor(color), transform: 'translateX(-50%)' }"
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
        @change="onColorChange"
      >

      <!-- Intensity Slider Modal/Popup -->
      <div v-if="pickerState.display" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 rounded-lg" @click.self="closePicker">
        <div class="bg-bg-sec border border-border p-6 w-80 shadow-2xl rounded-lg">
            <h3 class="text-sm font-bold uppercase text-accent mb-4">Edit Color</h3>
            
            <div class="mb-4">
                <label class="text-[10px] uppercase font-bold text-text-sec block mb-2">Color</label>
                <div class="flex gap-2 h-10">
                    <div class="w-10 h-10 border border-border" :style="{ backgroundColor: pickerState.previewColor }"></div>
                    <button @click="openNativeColorPicker" class="flex-1 border border-border hover:bg-bg-main text-xs font-bold uppercase transition-colors">Pick Color</button>
                </div>
            </div>

            <div class="mb-6">
                <div class="flex justify-between mb-2">
                    <label class="text-[10px] uppercase font-bold text-text-sec">Intensity (Alpha)</label>
                    <span class="text-[10px] font-mono">{{ selectedColorAlpha.toFixed(2) }}</span>
                </div>
                <input type="range" v-model.number="selectedColorAlpha" min="0" max="1" step="0.01" class="w-full accent-accent" @input="updateSelectedColor">
            </div>

            <div class="flex justify-between">
                 <button @click="closePicker" class="px-4 py-2 border border-border hover:bg-bg-main text-xs font-bold uppercase">Done</button>
                 <button @click="deleteSelectedStop" class="px-4 py-2 bg-red-500/10 text-red-500 border border-red-500/50 hover:bg-red-500/20 text-xs font-bold uppercase">Delete</button>
            </div>
        </div>
      </div>
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
const selectedColorAlpha = ref(1.0); // State for the slider

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
  display: false,
  frameIndex: -1,
  colorIndex: -1,
  previewColor: 'rgba(0,0,0,1)'
});

// --- METHODS ---
function getPreviewColor(colorObj) {
    const parts = colorObj.color.split(',');
    if (parts.length === 3) return `rgb(${colorObj.color})`;
    return `rgba(${colorObj.color})`;
}

// --- EXPORT / IMPORT ---
const copyFeedback = ref('');

function downloadJson() {
  const json = JSON.stringify(animation, null, 4);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${animation.name || 'led_animation'}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

async function copyJson() {
  try {
    await navigator.clipboard.writeText(JSON.stringify(animation, null, 4));
    copyFeedback.value = 'Copied!';
    setTimeout(() => { copyFeedback.value = ''; }, 1500);
  } catch (e) {
    copyFeedback.value = 'Error';
    setTimeout(() => { copyFeedback.value = ''; }, 1500);
  }
}

function importJson() {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json,application/json';
  input.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      const text = await file.text();
      const data = JSON.parse(text);
      if (data.frames && Array.isArray(data.frames)) {
        animation.name = data.name || 'Imported Animation';
        animation.frames = data.frames;
      } else {
        alert('Invalid animation file: missing frames array');
      }
    } catch (err) {
      alert('Failed to parse JSON file: ' + err.message);
    }
  };
  input.click();
}

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
  // Support RGB and RGBA in gradient
  const stops = sorted.map((c) => {
      const parts = c.color.split(',');
      if (parts.length === 3) return `rgb(${c.color}) ${c.position}%`;
      return `rgba(${c.color}) ${c.position}%`;
  }).join(', ');
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
  
  const colorObj = animation.frames[fIdx].colors[cIdx];
  const parts = colorObj.color.split(',').map(Number);
  
  // Set initial alpha
  selectedColorAlpha.value = parts.length > 3 ? parts[3] : 1.0;
  
  // Update preview
  updatePickerPreview();
  pickerState.display = true;
  
  // Sync hidden picker
  const r = parts[0];
  const g = parts[1];
  const b = parts[2];
  const hex = "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  if (colorPicker.value) colorPicker.value.value = hex;
}

function closePicker() {
    pickerState.display = false;
    pickerState.frameIndex = -1;
    pickerState.colorIndex = -1;
}

function openNativeColorPicker() {
    if (colorPicker.value) {
        colorPicker.value.click();
    }
}

function updatePickerPreview() {
    if (pickerState.frameIndex === -1) return;
    const colorStr = animation.frames[pickerState.frameIndex].colors[pickerState.colorIndex].color;
    const parts = colorStr.split(',');
    if (parts.length === 3) pickerState.previewColor = `rgb(${colorStr})`;
    else pickerState.previewColor = `rgba(${colorStr})`;
}

function updateSelectedColor() {
     if (pickerState.frameIndex === -1) return;
     
     // Get current RGB from the model (assuming it's up to date from color picker or init)
     const currentStr = animation.frames[pickerState.frameIndex].colors[pickerState.colorIndex].color;
     const parts = currentStr.split(',').map(Number);
     
     // Reconstruct with new alpha
     const r = parts[0];
     const g = parts[1];
     const b = parts[2];
     const a = selectedColorAlpha.value;
     
     // Update model to r,g,b,a
     // Use minimal float precision for cleaner JSON
     const aStr = a === 1 ? '1' : parseFloat(a.toFixed(3)); 
     
     if (a === 1) {
          animation.frames[pickerState.frameIndex].colors[pickerState.colorIndex].color = `${r},${g},${b}`;
     } else {
          animation.frames[pickerState.frameIndex].colors[pickerState.colorIndex].color = `${r},${g},${b},${aStr}`;
     }
     
     updatePickerPreview();
}

function onColorPicked(e) {
    if (pickerState.frameIndex === -1) return;
    
    const hex = e.target.value;
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    
    // Preserve current alpha
    const a = selectedColorAlpha.value;
    const aStr = a === 1 ? '1' : parseFloat(a.toFixed(3));
    
    if (a === 1) {
        animation.frames[pickerState.frameIndex].colors[pickerState.colorIndex].color = `${r},${g},${b}`;
    } else {
        animation.frames[pickerState.frameIndex].colors[pickerState.colorIndex].color = `${r},${g},${b},${aStr}`;
    }
    updatePickerPreview();
}

// Optional: triggered when picker closes if using native UI, but we use input event
function onColorChange(e) {
    onColorPicked(e);
}

function deleteSelectedStop() {
    if (pickerState.frameIndex !== -1) {
        removeStop(pickerState.frameIndex, pickerState.colorIndex);
        closePicker();
    }
}


// --- PREVIEW PLAYER ---
function parseColor(colorStr) {
    if (!colorStr) return [0, 0, 0, 1];
    const parts = colorStr.split(',').map(Number);
    if (parts.length === 3) return [...parts, 1]; // Default alpha 1
    return parts;
}

function lerp(start, end, t) {
    return start + (end - start) * t;
}

function interpolateColorRGBA(c1, c2, t) {
    const r = Math.round(lerp(c1[0], c2[0], t));
    const g = Math.round(lerp(c1[1], c2[1], t));
    const b = Math.round(lerp(c1[2], c2[2], t));
    const a = lerp(c1[3], c2[3], t);
    return [r, g, b, a];
}

function lerpColor(c1, c2, t) {
   const [r, g, b, a] = interpolateColorRGBA(c1, c2, t);
   return `rgba(${r},${g},${b},${a})`;
}


// Calculate pixels for a specific frame configuration
function calculatePixelsForFrame(frame) {
    const stops = frame.colors.map(c => ({
        pos: c.position,
        rgb: parseColor(c.color)
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
        const a = start.rgb[3] + (end.rgb[3] - start.rgb[3]) * ratio;
        
        pixels.push([r, g, b, a]); 
    }
    return pixels;
}

async function playPreview() {
    if (isPlaying.value) return;
    isPlaying.value = true;
    
    let frameIdx = 0;
    
    const loop = async () => {
        if (!isPlaying.value) return;
        
        // Safety check if frames exist
        if (animation.frames.length === 0) {
             stopPreview();
             return;
        }

        const currentFrame = animation.frames[frameIdx];
        const nextIdx = (frameIdx + 1) % animation.frames.length;
        const nextFrame = animation.frames[nextIdx];
        
        // Calculate start and end states for pixels
        const startPixels = calculatePixelsForFrame(currentFrame);
        const endPixels = calculatePixelsForFrame(nextFrame);
        
        const duration = currentFrame.time > 0 ? currentFrame.time : 100; // Minimum duration safety
        const startTime = performance.now();
        
        // Animation Loop for this transition
        // We use a promise to await the completion of this segment
        await new Promise(resolve => {
            const tick = (now) => {
                if (!isPlaying.value) {
                    resolve();
                    return;
                }
                
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1.0);
                
                // Render interpolated pixels
                const rendered = startPixels.map((p1, i) => {
                    const p2 = endPixels[i];
                    const rawColor = interpolateColorRGBA(p1, p2, progress);
                    const finalAlpha = rawColor[3];
                    return `rgba(${rawColor[0]}, ${rawColor[1]}, ${rawColor[2]}, ${finalAlpha})`;
                });
                previewPixels.value = rendered;
                
                if (progress < 1.0) {
                    requestAnimationFrame(tick);
                } else {
                    resolve();
                }
            };
            requestAnimationFrame(tick);
        });
        
        // Move to next frame
        if (isPlaying.value) {
            frameIdx = nextIdx;
            loop(); // Recursion (could use while loop but this is cleaner for async)
        }
    };
    
    loop();
}

function stopPreview() {
    isPlaying.value = false;
    // Reset to black? Or keep last state? Keeping last state is fine.
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
  @apply font-mono text-[11px] p-4 border border-border whitespace-pre-wrap;
  background-color: #1e1e1e;
  color: #9cdcfe;
}
</style>
