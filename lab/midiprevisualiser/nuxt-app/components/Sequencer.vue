<template>
  <div class="sequencer">
    <!-- Piano Roll (left sidebar) -->
    <div class="piano-roll" ref="pianoRollRef">
      <div class="piano-keys" :style="{ height: totalHeight + 'px' }">
        <div 
          v-for="note in noteRange" 
          :key="note"
          class="piano-key"
          :class="{ 'black-key': isBlackKey(note) }"
          :style="{ height: noteHeight + 'px' }"
        >
          <span v-if="note % 12 === 0" class="note-label">C{{ Math.floor(note / 12) - 1 }}</span>
        </div>
      </div>
    </div>
    
    <!-- Grid (main area) -->
    <div 
      class="grid-container" 
      ref="gridRef"
      @scroll="onGridScroll"
      @wheel="onWheel"
    >
      <div 
        class="grid" 
        :style="{ 
          width: gridWidth + 'px', 
          height: totalHeight + 'px' 
        }"
      >
        <!-- Grid lines -->
        <div class="grid-lines">
          <div 
            v-for="beat in beats" 
            :key="beat"
            class="grid-line"
            :class="{ 'bar-line': beat % 4 === 0 }"
            :style="{ left: beat * beatWidth + 'px' }"
          ></div>
        </div>
        
        <!-- Notes -->
        <div 
          v-for="(note, index) in allNotes" 
          :key="index"
          class="midi-note"
          :class="{ hover: hoveredNote === index }"
          :style="getNoteStyle(note)"
          @mouseenter="hoveredNote = index"
          @mouseleave="hoveredNote = null"
        >
          <span class="note-info" v-if="hoveredNote === index">
            {{ getNoteName(note.note) }} | Ch{{ note.channel + 1 }} | Vel{{ note.velocity }}
          </span>
        </div>
      </div>
    </div>
    
    <!-- Zoom Controls -->
    <div class="zoom-controls glass-panel">
      <button class="zoom-btn" @click="zoomOut">−</button>
      <span class="zoom-level">{{ Math.round(zoom * 100) }}%</span>
      <button class="zoom-btn" @click="zoomIn">+</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useMidiParser, type MidiFile, type MidiNote } from '~/composables/useMidiParser'

const props = defineProps<{
  midiData: MidiFile
}>()

const { getNoteName, isBlackKey } = useMidiParser()

// Refs
const gridRef = ref<HTMLElement | null>(null)
const pianoRollRef = ref<HTMLElement | null>(null)
const hoveredNote = ref<number | null>(null)

// View settings
const zoom = ref(1)
const noteHeight = 14
const beatWidth = computed(() => 60 * zoom.value)

// Channel colors
const channelColors = [
  '#ff3366', '#33ff99', '#3399ff', '#ff9933',
  '#cc33ff', '#ffff33', '#33ffff', '#ff6633',
  '#66ff33', '#ff33cc', '#33ccff', '#ffcc33',
  '#9933ff', '#33ff66', '#ff3399', '#99ff33'
]

// Computed values
const noteRange = computed(() => {
  const min = Math.max(0, props.midiData.noteRange.min - 2)
  const max = Math.min(127, props.midiData.noteRange.max + 2)
  // Return array from max to min (high notes at top)
  return Array.from({ length: max - min + 1 }, (_, i) => max - i)
})

const totalHeight = computed(() => noteRange.value.length * noteHeight)

const allNotes = computed(() => {
  return props.midiData.tracks.flatMap(track => track.notes)
})

const totalBeats = computed(() => {
  return Math.ceil(props.midiData.totalTicks / props.midiData.ticksPerBeat) + 4
})

const beats = computed(() => {
  return Array.from({ length: totalBeats.value }, (_, i) => i)
})

const gridWidth = computed(() => totalBeats.value * beatWidth.value)

// Methods
function getNoteStyle(note: MidiNote) {
  const minNote = noteRange.value[noteRange.value.length - 1]
  const maxNote = noteRange.value[0]
  
  // Position from top (high notes at top)
  const noteIndex = maxNote - note.note
  const top = noteIndex * noteHeight
  
  // Horizontal position based on time
  const left = (note.startTick / props.midiData.ticksPerBeat) * beatWidth.value
  const width = Math.max(4, (note.duration / props.midiData.ticksPerBeat) * beatWidth.value)
  
  // Color based on channel, brightness based on velocity
  const baseColor = channelColors[note.channel % 16]
  const brightness = 0.5 + (note.velocity / 127) * 0.5
  
  return {
    top: `${top}px`,
    left: `${left}px`,
    width: `${width}px`,
    height: `${noteHeight - 2}px`,
    backgroundColor: baseColor,
    opacity: brightness
  }
}

function onGridScroll() {
  // Sync piano roll vertical scroll with grid
  if (gridRef.value && pianoRollRef.value) {
    pianoRollRef.value.scrollTop = gridRef.value.scrollTop
  }
}

function onWheel(e: WheelEvent) {
  if (e.ctrlKey || e.metaKey) {
    e.preventDefault()
    const delta = e.deltaY > 0 ? 0.9 : 1.1
    zoom.value = Math.max(0.25, Math.min(4, zoom.value * delta))
  }
}

function zoomIn() {
  zoom.value = Math.min(4, zoom.value * 1.25)
}

function zoomOut() {
  zoom.value = Math.max(0.25, zoom.value * 0.8)
}
</script>

<style scoped>
.sequencer {
  display: flex;
  height: 100%;
  position: relative;
  background: var(--bg-grid);
}

.piano-roll {
  width: var(--piano-key-width);
  flex-shrink: 0;
  overflow: hidden;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
}

.piano-keys {
  display: flex;
  flex-direction: column;
}

.piano-key {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
  border-bottom: 1px solid var(--grid-line);
  font-size: 10px;
  color: var(--text-secondary);
  background: linear-gradient(90deg, #1a1a25 0%, #252535 100%);
}

.piano-key.black-key {
  background: linear-gradient(90deg, #0a0a0f 0%, #151520 100%);
}

.note-label {
  font-weight: 600;
  color: var(--text-primary);
}

.grid-container {
  flex: 1;
  overflow: auto;
  position: relative;
}

.grid {
  position: relative;
  min-height: 100%;
}

.grid-lines {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.grid-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  background: var(--grid-line);
}

.grid-line.bar-line {
  background: var(--grid-bar);
}

.midi-note {
  position: absolute;
  border-radius: 3px;
  cursor: pointer;
  transition: transform 0.1s ease, box-shadow 0.1s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.midi-note:hover,
.midi-note.hover {
  transform: scale(1.05);
  box-shadow: 0 0 10px currentColor;
  z-index: 10;
}

.note-info {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.9);
  border-radius: 4px;
  font-size: 11px;
  white-space: nowrap;
  pointer-events: none;
  z-index: 100;
}

.zoom-controls {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
}

.zoom-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: none;
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.zoom-btn:hover {
  background: #353545;
}

.zoom-level {
  min-width: 50px;
  text-align: center;
  font-size: 13px;
  color: var(--text-secondary);
}
</style>
