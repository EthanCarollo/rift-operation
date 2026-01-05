import { useState } from '#app'

export type AppMode = 'Dream' | 'Nightmare'
export type WebcamMap = Record<string, string> // DeviceID -> CustomName

export const useRiftState = () => {
  const appMode = useState<AppMode | null>('rift-mode', () => null)
  // Store selected webcams as a map of ID -> Name
  const selectedWebcams = useState<WebcamMap>('rift-webcams', () => ({}))
  // Store webcam rotations as Map<DeviceID, RotationAngle>
  const webcamRotations = useState<Record<string, number>>('rift-webcams-rotations', () => ({}))
  // Store webcam filters as Map<DeviceID, {grayscale: boolean, fnaf: boolean}>
  const webcamFilters = useState<Record<string, { grayscale: boolean, fnaf: boolean }>>('rift-webcams-filters', () => ({}))

  const resetState = () => {
    appMode.value = null
    selectedWebcams.value = {}
    webcamRotations.value = {}
    webcamFilters.value = {}
  }

  return {
    appMode,
    selectedWebcams,
    webcamRotations,
    webcamFilters,
    resetState
  }
}
