<template>
  <div class="app-container">
    <!-- Header -->
    <header class="app-header glass-panel">
      <h1>🎹 MIDI Visualizer</h1>
      <div class="header-actions">
        <label class="btn btn-primary">
          <input type="file" accept=".mid,.midi" @change="handleFileSelect" hidden />
          📁 Load MIDI
        </label>
      </div>
    </header>
    
    <!-- Main Content -->
    <main class="app-main">
      <!-- Drop Zone (shown when no file loaded) -->
      <MidiDropZone 
        v-if="!midiData" 
        @file-loaded="handleMidiLoad" 
      />
      
      <!-- Sequencer (shown when file loaded) -->
      <Sequencer 
        v-else 
        :midi-data="midiData" 
      />
    </main>
    
    <!-- Footer -->
    <footer class="app-footer" v-if="midiData">
      <span>{{ midiData.tracks.length }} tracks</span>
      <span>•</span>
      <span>{{ midiData.ticksPerBeat }} ticks/beat</span>
      <span>•</span>
      <span>Notes: {{ midiData.noteRange.min }} - {{ midiData.noteRange.max }}</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMidiParser, type MidiFile } from '~/composables/useMidiParser'

const { parseMidi } = useMidiParser()
const midiData = ref<MidiFile | null>(null)

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    loadMidiFile(input.files[0])
  }
}

function handleMidiLoad(file: File) {
  loadMidiFile(file)
}

async function loadMidiFile(file: File) {
  try {
    const buffer = await file.arrayBuffer()
    midiData.value = parseMidi(buffer)
    console.log('Loaded MIDI:', midiData.value)
  } catch (error) {
    console.error('Failed to parse MIDI:', error)
    alert('Failed to parse MIDI file')
  }
}

// Try to load sample MIDI on mount
onMounted(async () => {
  try {
    const response = await fetch('/sample.mid')
    if (response.ok) {
      const buffer = await response.arrayBuffer()
      midiData.value = parseMidi(buffer)
    }
  } catch {
    // No sample file available, that's okay
  }
})
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  border-radius: 0;
  border-top: none;
  border-left: none;
  border-right: none;
}

.app-header h1 {
  font-size: 20px;
  font-weight: 600;
  background: linear-gradient(135deg, #fff, #3399ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.app-main {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.app-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 24px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  font-size: 13px;
  color: var(--text-secondary);
}
</style>
