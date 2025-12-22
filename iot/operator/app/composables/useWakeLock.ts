import { ref, onMounted, onUnmounted } from 'vue'

export function useWakeLock() {
  const isSupported = ref(false)
  const isActive = ref(false)
  let wakeLock: any = null

  const requestLock = async () => {
    if (!isSupported.value) return

    try {
      wakeLock = await (navigator as any).wakeLock.request('screen')
      isActive.value = true
      console.log('Wake Lock active')

      wakeLock.addEventListener('release', () => {
        isActive.value = false
        console.log('Wake Lock released')
      })
    } catch (err) {
      console.error(`Wake Lock failed: ${err}`)
      isActive.value = false
    }
  }

  const releaseLock = async () => {
    if (wakeLock) {
      await wakeLock.release()
      wakeLock = null
    }
  }

  const handleVisibilityChange = async () => {
    if (document.visibilityState === 'visible' && !isActive.value) {
      await requestLock()
    }
  }

  onMounted(() => {
    if ('wakeLock' in navigator) {
      isSupported.value = true
      requestLock()
      document.addEventListener('visibilitychange', handleVisibilityChange)
    } else {
      console.warn('Wake Lock API not supported in this browser.')
    }
  })

  onUnmounted(() => {
    document.removeEventListener('visibilitychange', handleVisibilityChange)
    releaseLock()
  })

  return {
    isSupported,
    isActive
  }
}
