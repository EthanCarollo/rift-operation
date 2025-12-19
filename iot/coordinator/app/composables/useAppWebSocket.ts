import { config } from '../../config.js'

export const useAppWebSocket = () => {
  const isConnected = useState<boolean>('websocket-connected', () => false)
  let socket: WebSocket | null = null
  let reconnectInterval: any = null

  const connect = () => {
    if (import.meta.server) return

    // Avoid multiple connections
    if (socket && (socket.readyState === WebSocket.CONNECTING || socket.readyState === WebSocket.OPEN)) return

    console.log('Connecting to WebSocket...', config.websocketUrl)
    
    try {
      socket = new WebSocket(config.websocketUrl)

      socket.onopen = () => {
        isConnected.value = true
        console.log('WebSocket Connected')
        if (reconnectInterval) {
          clearInterval(reconnectInterval)
          reconnectInterval = null
        }
      }

      socket.onclose = () => {
        isConnected.value = false
        console.log('WebSocket Disconnected')
        // Attempt reconnect if not already trying
        if (!reconnectInterval) {
          reconnectInterval = setInterval(() => {
            console.log('Reconnecting...')
            connect()
          }, 3000)
        }
      }

      socket.onerror = (error) => {
        console.error('WebSocket Error:', error)
        // Ensure close is called to trigger onclose and reconnection logic
        if (socket && socket.readyState !== WebSocket.CLOSED) {
             socket.close()
        }
      }
    } catch (e) {
      console.error('WebSocket Connection Failed:', e)
    }
  }

  return {
    isConnected,
    connect
  }
}
