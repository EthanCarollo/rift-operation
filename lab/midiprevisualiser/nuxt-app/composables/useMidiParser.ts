/**
 * MIDI File Parser Composable
 * Parses MIDI binary data and extracts note events
 */

export interface MidiNote {
  channel: number
  note: number
  velocity: number
  startTick: number
  endTick: number
  duration: number
}

export interface MidiTrack {
  name: string
  notes: MidiNote[]
  channel: number
}

export interface MidiFile {
  format: number
  ticksPerBeat: number
  tracks: MidiTrack[]
  totalTicks: number
  noteRange: { min: number; max: number }
}

// MIDI constants
const NOTE_ON = 0x90
const NOTE_OFF = 0x80

export function useMidiParser() {
  
  /**
   * Parse MIDI file from ArrayBuffer
   */
  function parseMidi(buffer: ArrayBuffer): MidiFile {
    const data = new Uint8Array(buffer)
    let pos = 0
    
    // Parse header
    const headerChunk = readChunk(data, pos)
    pos += 8 + headerChunk.length
    
    const headerView = new DataView(headerChunk.data.buffer, headerChunk.data.byteOffset)
    const format = headerView.getUint16(0)
    const numTracks = headerView.getUint16(2)
    const ticksPerBeat = headerView.getUint16(4)
    
    // Parse tracks
    const tracks: MidiTrack[] = []
    let totalTicks = 0
    let minNote = 127
    let maxNote = 0
    
    for (let t = 0; t < numTracks; t++) {
      if (pos >= data.length) break
      
      const trackChunk = readChunk(data, pos)
      pos += 8 + trackChunk.length
      
      if (trackChunk.type !== 'MTrk') continue
      
      const { notes, trackName, channel, lastTick } = parseTrack(trackChunk.data)
      
      if (notes.length > 0) {
        tracks.push({
          name: trackName || `Track ${t + 1}`,
          notes,
          channel
        })
        
        totalTicks = Math.max(totalTicks, lastTick)
        
        for (const note of notes) {
          minNote = Math.min(minNote, note.note)
          maxNote = Math.max(maxNote, note.note)
        }
      }
    }
    
    return {
      format,
      ticksPerBeat,
      tracks,
      totalTicks,
      noteRange: { min: minNote, max: maxNote }
    }
  }
  
  /**
   * Read a MIDI chunk (header or track)
   */
  function readChunk(data: Uint8Array, pos: number) {
    const type = String.fromCharCode(data[pos], data[pos + 1], data[pos + 2], data[pos + 3])
    const length = (data[pos + 4] << 24) | (data[pos + 5] << 16) | (data[pos + 6] << 8) | data[pos + 7]
    const chunkData = data.slice(pos + 8, pos + 8 + length)
    return { type, length, data: chunkData }
  }
  
  /**
   * Parse a MIDI track
   */
  function parseTrack(data: Uint8Array) {
    const notes: MidiNote[] = []
    const activeNotes = new Map<string, { note: number; channel: number; velocity: number; startTick: number }>()
    let pos = 0
    let tick = 0
    let trackName = ''
    let lastStatus = 0
    let trackChannel = 0
    
    while (pos < data.length) {
      // Read delta time (variable length)
      let delta = 0
      let byte: number
      do {
        byte = data[pos++]
        delta = (delta << 7) | (byte & 0x7f)
      } while (byte & 0x80)
      
      tick += delta
      
      // Read status byte
      let status = data[pos]
      
      // Running status
      if (status < 0x80) {
        status = lastStatus
      } else {
        pos++
        lastStatus = status
      }
      
      const type = status & 0xf0
      const channel = status & 0x0f
      
      if (type === NOTE_ON || type === NOTE_OFF) {
        const note = data[pos++]
        const velocity = data[pos++]
        const key = `${channel}-${note}`
        
        if (type === NOTE_ON && velocity > 0) {
          activeNotes.set(key, { note, channel, velocity, startTick: tick })
          trackChannel = channel
        } else {
          const active = activeNotes.get(key)
          if (active) {
            notes.push({
              channel: active.channel,
              note: active.note,
              velocity: active.velocity,
              startTick: active.startTick,
              endTick: tick,
              duration: tick - active.startTick
            })
            activeNotes.delete(key)
          }
        }
      } else if (type === 0xa0 || type === 0xb0 || type === 0xe0) {
        // Polyphonic/Control/Pitch - 2 data bytes
        pos += 2
      } else if (type === 0xc0 || type === 0xd0) {
        // Program/Channel pressure - 1 data byte
        pos += 1
      } else if (status === 0xff) {
        // Meta event
        const metaType = data[pos++]
        let metaLength = 0
        do {
          byte = data[pos++]
          metaLength = (metaLength << 7) | (byte & 0x7f)
        } while (byte & 0x80)
        
        if (metaType === 0x03) {
          // Track name
          trackName = String.fromCharCode(...data.slice(pos, pos + metaLength))
        }
        
        pos += metaLength
      } else if (status === 0xf0 || status === 0xf7) {
        // SysEx
        let sysexLength = 0
        do {
          byte = data[pos++]
          sysexLength = (sysexLength << 7) | (byte & 0x7f)
        } while (byte & 0x80)
        pos += sysexLength
      }
    }
    
    return { notes, trackName, channel: trackChannel, lastTick: tick }
  }
  
  /**
   * Get note name from MIDI note number
   */
  function getNoteName(noteNumber: number): string {
    const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    const octave = Math.floor(noteNumber / 12) - 1
    const note = notes[noteNumber % 12]
    return `${note}${octave}`
  }
  
  /**
   * Check if a note is a black key
   */
  function isBlackKey(noteNumber: number): boolean {
    const note = noteNumber % 12
    return [1, 3, 6, 8, 10].includes(note)
  }
  
  return {
    parseMidi,
    getNoteName,
    isBlackKey
  }
}
