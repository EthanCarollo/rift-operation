<template>
  <div 
    class="drop-zone"
    :class="{ dragging: isDragging }"
    @dragenter.prevent="onDragEnter"
    @dragover.prevent
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
  >
    <div class="drop-zone-content">
      <div class="drop-icon">🎵</div>
      <h2>Drop a MIDI file here</h2>
      <p>or click to browse</p>
      <label class="btn btn-primary">
        <input type="file" accept=".mid,.midi" @change="onFileSelect" hidden />
        Choose File
      </label>
    </div>
    
    <!-- Decorative grid background -->
    <div class="grid-bg"></div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  (e: 'file-loaded', file: File): void
}>()

const isDragging = ref(false)

function onDragEnter() {
  isDragging.value = true
}

function onDragLeave(e: DragEvent) {
  // Only leave if actually leaving the drop zone
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  if (
    e.clientX < rect.left || 
    e.clientX > rect.right || 
    e.clientY < rect.top || 
    e.clientY > rect.bottom
  ) {
    isDragging.value = false
  }
}

function onDrop(e: DragEvent) {
  isDragging.value = false
  const files = e.dataTransfer?.files
  if (files && files[0]) {
    const file = files[0]
    if (file.name.match(/\.(mid|midi)$/i)) {
      emit('file-loaded', file)
    } else {
      alert('Please drop a MIDI file (.mid or .midi)')
    }
  }
}

function onFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    emit('file-loaded', input.files[0])
  }
}
</script>

<style scoped>
.drop-zone {
  position: absolute;
  inset: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed var(--border-color);
  border-radius: 16px;
  background: var(--bg-secondary);
  transition: all 0.3s ease;
  overflow: hidden;
  cursor: pointer;
}

.drop-zone:hover {
  border-color: rgba(51, 153, 255, 0.5);
  background: rgba(51, 153, 255, 0.05);
}

.drop-zone.dragging {
  border-color: var(--channel-2);
  background: rgba(51, 153, 255, 0.1);
  box-shadow: 0 0 40px rgba(51, 153, 255, 0.2);
}

.drop-zone-content {
  position: relative;
  z-index: 1;
  text-align: center;
  animation: slideIn 0.5s ease;
}

.drop-icon {
  font-size: 64px;
  margin-bottom: 16px;
  animation: pulse 2s ease-in-out infinite;
}

.drop-zone-content h2 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.drop-zone-content p {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.grid-bg {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(var(--grid-line) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
  background-size: 30px 20px;
  opacity: 0.5;
  pointer-events: none;
}
</style>
