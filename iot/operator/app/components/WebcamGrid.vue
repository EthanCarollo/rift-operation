<template>
  <div class="h-full w-full flex flex-col font-mono" :class="{'p-6': mode === 'selection'}">
    
    <!-- HEADER (Visible in Selection Mode) -->
    <div v-if="mode === 'selection'" class="flex items-end justify-between mb-8 border-b border-[var(--border)] pb-4 flex-none">
      <div>
        <h2 class="text-xl font-bold uppercase tracking-tight text-[var(--text-main)]">
          System Cameras
        </h2>
        <p class="text-xs text-[var(--text-sec)] uppercase mt-1">
          Select active feeds & Assign Designators
        </p>
      </div>
      <div class="flex gap-4">
        <button 
          @click="() => refreshDevices(true)"
          class="px-4 py-2 border border-[var(--border)] bg-[var(--bg-sec)] hover:bg-[var(--bg-main)] hover:border-[var(--border-focus)] text-xs font-bold uppercase transition-all flex items-center gap-2"
        >
          <span>Refresh</span>
        </button>
        <button 
          v-if="selectionCount > 0"
          @click="confirmSelection"
          class="px-6 py-2 bg-[var(--accent)] text-[var(--accent-text)] text-xs font-bold uppercase hover:opacity-90 transition-all flex items-center gap-2"
        >
          <span>Continue ({{ selectionCount }})</span> →
        </button>
      </div>
    </div>

    <!-- Permission Error -->
    <div v-if="error" class="flex-none border border-red-500 bg-red-500/5 p-4 mb-6 text-red-500 text-center text-xs font-bold uppercase transition-all">
      <div class="text-lg mb-1">{{ error }}</div>
      <div v-if="errorDetails" class="text-[10px] opacity-70 normal-case font-mono bg-black/20 p-2 rounded mb-2 select-text ">{{ errorDetails }}</div>
      
      <div class="flex gap-4 justify-center">
        <button @click="requestPermissions" class="underline hover:text-white">Retry Access</button>
        <button @click="showDebug = !showDebug" class="underline hover:text-white opacity-70">
            {{ showDebug ? 'Hide Debug' : 'Show System Dump' }}
        </button>
      </div>

      <!-- Raw Device Dump -->
      <div v-if="showDebug" class="mt-4 text-left bg-black/50 p-4 rounded font-mono text-[10px] overflow-x-auto whitespace-pre text-gray-300 select-text card border border-white/10">
        <div class="font-bold text-white mb-2 border-b border-white/20 pb-1">BROWSER DEVICE DUMP:</div>
        <div v-if="debugDevices.length === 0">No devices enumerated yet.</div>
        <div v-for="(d, i) in debugDevices" :key="i" class="mb-1 border-b border-white/5 pb-1">
            <span class="text-blue-400">[{{ d.kind }}]</span> 
            <span :class="d.label ? 'text-green-400' : 'text-red-500'">{{ d.label ? d.label : '[EMPTY_LABEL (NO PERM)]' }}</span>
            <span class="text-gray-500 ml-2">ID: {{ d.deviceId.slice(0, 8) }}...</span>
        </div>
      </div>
    </div>

    <!-- Grid Container -->
    <div 
      class="flex-1 overflow-hidden" 
      :class="{
        'grid gap-4 auto-rows-min overflow-y-auto grid-cols-1 md:grid-cols-2': mode === 'selection',
        'grid h-full w-full': mode === 'view'
      }"
      :style="mode === 'view' ? viewGridStyle : {}"
    >
      <div 
        v-for="(cam, index) in displayList" 
        :key="cam.deviceId"
        class="relative bg-black group overflow-hidden border transition-all"
        :class="getCellClass(cam.deviceId)"
        :style="getCellStyle(index)"
        @click="handleCellClick(cam.deviceId)"
      >
        <!-- Video Element -->
        <video 
          :ref="(el) => setVideoRef(el as HTMLVideoElement, cam.deviceId)"
          autoplay 
          playsinline 
          muted 
          class="absolute inset-0 w-full h-full object-cover transition-transform duration-300"
          :style="{ transform: `rotate(${rotations[cam.deviceId] || 0}deg)` }"
          :class="{
            'opacity-50 group-hover:opacity-80': mode === 'selection' && !currentSelection[cam.deviceId], 
            'opacity-100': currentSelection[cam.deviceId] || mode === 'view',
            'grayscale': filters[cam.deviceId]?.grayscale, 
            'contrast-125 brightness-90': true /* SURVEILLANCE FILTER BASE */
          }"
        ></video>
        
        <!-- FNAF OVERLAY -->
        <div v-if="filters[cam.deviceId]?.fnaf" class="pointer-events-none absolute inset-0 z-0 fnaf-overlay"></div>

        <!-- SELECTION MODE UI -->
        <div v-if="mode === 'selection'" class="absolute inset-x-0 bottom-0 p-3 bg-black/90 border-t border-white/10 z-10 flex flex-col gap-2">
            <div class="flex justify-between items-center">
                 <span class="text-[10px] text-gray-400 uppercase truncate max-w-[70%]">
                    {{ cam.label || 'CAM_' + cam.deviceId.slice(0, 4) }}
                 </span>
                 <!-- Checkbox Indicator -->
                 <div 
                    class="w-4 h-4 border border-white/50 transition-colors flex items-center justify-center"
                    :class="{'bg-[var(--success)] border-transparent text-black': currentSelection[cam.deviceId]}"
                  >
                    <span v-if="currentSelection[cam.deviceId]" class="text-[10px] font-bold">✓</span>
                  </div>
            </div>
            
            <!-- Renaming Input (Only if selected) -->
            <div v-if="currentSelection[cam.deviceId] !== undefined" @click.stop class="flex flex-col gap-2">
                <input 
                    type="text" 
                    v-model="currentSelection[cam.deviceId]"
                    class="w-full bg-white/10 border border-white/20 text-white text-xs px-2 py-1 focus:border-[var(--success)] focus:outline-none placeholder-white/30 font-bold uppercase"
                    placeholder="ENTER DESIGNATOR"
                />
                <!-- Rotation Control -->
                <button 
                    @click.stop="rotateCamera(cam.deviceId)"
                    class="w-full text-[10px] bg-white/10 hover:bg-white/20 text-gray-300 px-2 py-1 uppercase font-bold border border-white/20 transition-colors flex justify-between"
                >
                    <span>Rotate</span>
                    <span>{{ rotations[cam.deviceId] || 0 }}°</span>
                </button>

                <!-- Filter Controls -->
                <div class="flex gap-2">
                    <button 
                        @click.stop="toggleFilter(cam.deviceId, 'grayscale')"
                        class="flex-1 text-[10px] bg-white/10 hover:bg-white/20 text-gray-300 px-2 py-1 uppercase font-bold border border-white/20 transition-colors"
                        :class="{'bg-[var(--accent)] text-[var(--accent-text)] border-[var(--accent)]': filters[cam.deviceId]?.grayscale}"
                    >
                        B&W
                    </button>
                    <button 
                        @click.stop="toggleFilter(cam.deviceId, 'fnaf')"
                        class="flex-1 text-[10px] bg-white/10 hover:bg-white/20 text-gray-300 px-2 py-1 uppercase font-bold border border-white/20 transition-colors"
                         :class="{'bg-[var(--accent)] text-[var(--accent-text)] border-[var(--accent)]': filters[cam.deviceId]?.fnaf}"
                    >
                        FNAF
                    </button>
                </div>
            </div>
        </div>


        <!-- VIEW MODE OVERLAY -->
        <div 
          v-if="mode === 'view'"
          class="absolute top-4 left-4 z-20"
        >
            <div class="bg-black/80 border border-white/20 px-3 py-1 flex flex-col">
                <span class="text-[14px] font-bold text-white uppercase tracking-widest font-mono leading-none mb-1">
                    {{ customNames[cam.deviceId] || 'UNKNOWN_CAM' }}
                </span>
                <span class="text-[8px] text-[var(--success)] uppercase tracking-wide font-mono animate-pulse">
                    ● {{ props.initialSelected ? 'REC' : 'LIVE' }}
                </span>
            </div>
            <!-- Rotation Control Removed from Monitor -->
        </div>

      </div>
    </div>

    <!-- Empty State -->
    <div v-if="webcams.length === 0 && !error" class="flex-1 flex flex-col items-center justify-center text-[var(--text-sec)] min-h-[300px]">
      <div class="text-4xl mb-4 grayscale opacity-50">📷</div>
      <p class="text-sm uppercase font-bold">No Signal</p>
      <p class="text-xs">Check connections</p>
    </div>
    
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps<{
  mode: 'selection' | 'view'
  initialSelected?: Record<string, string>
  initialRotations?: Record<string, number>
  initialFilters?: Record<string, { grayscale: boolean, fnaf: boolean }>
}>()

const emit = defineEmits<{
  (e: 'continue', selection: Record<string, string>, rotations: Record<string, number>, filters: Record<string, { grayscale: boolean, fnaf: boolean }>): void
}>()

interface WebcamInfo {
  deviceId: string
  label: string
}

const webcams = ref<WebcamInfo[]>([])
const streams = ref<Map<string, MediaStream>>(new Map())
const error = ref<string | null>(null)
const errorDetails = ref<string | null>(null)
const showDebug = ref(false)
const debugDevices = ref<MediaDeviceInfo[]>([])
const videoRefs = ref<Map<string, HTMLVideoElement>>(new Map())

// State for selection mode: Map<ID, CustomName>
// In view mode, we use props.initialSelected directly
const currentSelection = ref<Record<string, string>>({ ...props.initialSelected })

// State for rotation: Map<ID, Angle>
const rotations = ref<Record<string, number>>({ ...props.initialRotations })

// State for filters: Map<ID, Config>
const filters = ref<Record<string, { grayscale: boolean, fnaf: boolean }>>({ ...props.initialFilters })

const customNames = computed(() => {
    return props.mode === 'view' ? (props.initialSelected || {}) : currentSelection.value
})

const selectionCount = computed(() => Object.keys(currentSelection.value).length)

// Determine which cameras to show
const displayList = computed(() => {
  if (props.mode === 'view') {
    const selectedIds = Object.keys(props.initialSelected || {})
    return webcams.value.filter(c => selectedIds.includes(c.deviceId))
  }
  return webcams.value
})

// Dynamic Tiling (Same as before)
const viewGridStyle = computed(() => {
  const count = displayList.value.length
  if (count === 0) return {}
  
  // Bento Layout for 3 items: 2 columns (Large Left, Stacked Right)
  if (count === 3) {
      return {
          gridTemplateColumns: '2fr 1fr',
          gridTemplateRows: '1fr 1fr'
      }
  }

  const cols = Math.ceil(Math.sqrt(count))
  const rows = Math.ceil(count / cols)
  return {
    gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))`,
    gridTemplateRows: `repeat(${rows}, minmax(0, 1fr))`
  }
})

const getCellStyle = (index: number) => {
    if (props.mode === 'view' && displayList.value.length === 3 && index === 0) {
        return { gridRow: 'span 2' }
    }
    return {}
}

const getCellClass = (id: string) => {
  if (props.mode === 'view') {
    return 'border-r border-b border-black'
  }
  return currentSelection.value[id]
    ? 'border-[var(--success)] shadow-lg ring-1 ring-[var(--success)] aspect-video' 
    : 'border-[var(--border)] hover:border-[var(--border-focus)] cursor-pointer aspect-video'
}

const handleCellClick = (id: string) => {
    if (props.mode === 'view') return

    if (currentSelection.value[id]) {
        delete currentSelection.value[id]
    } else {
        // Default name
        const cam = webcams.value.find(c => c.deviceId === id)
        const count = Object.keys(currentSelection.value).length + 1
        // Create a default designator like "CAM_01"
        currentSelection.value[id] = `CAM_FEED_${String(count).padStart(2, '0')}`
    }
}

const confirmSelection = () => {
    emit('continue', currentSelection.value, rotations.value, filters.value)
}

const toggleFilter = (deviceId: string, type: 'grayscale' | 'fnaf') => {
    if (!filters.value[deviceId]) {
        filters.value[deviceId] = { grayscale: false, fnaf: false }
    }
    filters.value[deviceId][type] = !filters.value[deviceId][type]
}

const rotateCamera = (deviceId: string) => {
    const current = rotations.value[deviceId] || 0
    rotations.value[deviceId] = (current + 90) % 360
}

// ... Camera logic ...
const setVideoRef = (el: HTMLVideoElement, id: string) => {
  if (el) {
    videoRefs.value.set(id, el)
    if (streams.value.has(id)) {
      el.srcObject = streams.value.get(id)!
    }
  }
}

const requestPermissions = async () => {
  try {
    error.value = null
    const stream = await navigator.mediaDevices.getUserMedia({ video: true })
    stream.getTracks().forEach(t => t.stop())
    await refreshDevices()
  } catch (err: any) {
    console.error(err)
    error.value = "ACCESS DENIED"
    errorDetails.value = `${err.name}: ${err.message}`
    // Try to enumerate anyway to see if hardware exists (labels will be empty)
    await refreshDevices(false)
  }
}

const refreshDevices = async (startStreams = true) => {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    const videoInputs = devices.filter(d => d.kind === 'videoinput')
    
    debugDevices.value = videoInputs // Store for debug view
    
    // Stop all streams first to ensure clean state
    stopAllStreams()
    
    webcams.value = videoInputs.map(d => ({
      deviceId: d.deviceId,
      label: d.label || `CAM_${d.deviceId.slice(0, 4)}`
    }))

    if (!startStreams) return

    const toStart = props.mode === 'view' ? displayList.value : webcams.value
    
    // Start streams SEQUENTIALLY to prevent USB bandwidth issues on Windows
    for (const cam of toStart) {
      console.log(`Starting stream for ${cam.label || cam.deviceId}...`)
      await startStream(cam.deviceId)
      // Add delay between starts to allow USB bus to settle
      await new Promise(resolve => setTimeout(resolve, 500))
    }
  } catch (err) {
    console.error('Error refreshing devices:', err)
  }
}

const startStream = async (deviceId: string) => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { 
        deviceId: { exact: deviceId },
        width: { ideal: 1280 }, // HD quality (only 1 cam per sector)
        height: { ideal: 720 },
        frameRate: { ideal: 30, max: 30 } // Smooth 30fps
      }
    })
    streams.value.set(deviceId, stream)
    const videoEl = videoRefs.value.get(deviceId)
    if (videoEl) videoEl.srcObject = stream
  } catch (err) {
    console.warn(`Failed to start stream ${deviceId}`, err)
  }
}

const stopAllStreams = () => {
  streams.value.forEach(s => s.getTracks().forEach(t => t.stop()))
  streams.value.clear()
}

onMounted(() => requestPermissions())
onUnmounted(() => stopAllStreams())

watch(() => props.mode, () => refreshDevices())
</script>

<style scoped>
.fnaf-overlay {
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.15),
    rgba(0, 0, 0, 0.15) 1px,
    transparent 1px,
    transparent 2px
  );
  background-size: 100% 4px;
  animation: scanlines 1s linear infinite;
  box-shadow: inset 0 0 50px rgba(0,0,0,0.5);
}

@keyframes scanlines {
    0% { background-position: 0 0; }
    100% { background-position: 0 4px; }
}
</style>
