import { useState } from '#app'

export type AppMode = 'Dream' | 'Nightmare'
export type WebcamMap = Record<string, string> // DeviceID -> CustomName

export const useRiftState = () => {
  const appMode = useState<AppMode | null>('rift-mode', () => null)
  // Store selected webcams as a map of ID -> Name
  const selectedWebcams = useState<WebcamMap>('rift-webcams', () => ({}))

  const resetState = () => {
    appMode.value = null
    selectedWebcams.value = {}
  }

  return {
    appMode,
    selectedWebcams,
    resetState
  }
}
