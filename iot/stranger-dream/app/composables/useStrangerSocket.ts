export const useStrangerSocket = () => {
    const isConnected = useState<boolean>('socket-connected', () => false)
    const messages = useState<any[]>('socket-messages', () => [])
    const strangerState = useState<string>('stranger-state', () => 'inactive')
    let socket: WebSocket | null = null
    let reconnectTimer: any = null

    const connect = () => {
        if (socket?.readyState === WebSocket.OPEN) return

        try {
            socket = new WebSocket('ws://192.168.10.7:8000/ws')

            socket.onopen = () => {
                console.log('WebSocket Connected')
                isConnected.value = true
                if (reconnectTimer) {
                    clearTimeout(reconnectTimer)
                    reconnectTimer = null
                }
                // Send presence message to websocket panel
                socket?.send(JSON.stringify({
                    device_id: 'stranger-dream-instruction'
                }))
            }

            socket.onclose = () => {
                console.log('WebSocket Disconnected')
                isConnected.value = false
                socket = null
                // Reconnect after 3 seconds
                reconnectTimer = setTimeout(connect, 3000)
            }

            socket.onerror = (error) => {
                console.error('WebSocket Error:', error)
            }

            socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data)
                    console.log('Received:', data)
                    messages.value.push(data)
                    
                    if (data.stranger_state) {
                        strangerState.value = data.stranger_state
                    }
                    
                    // Keep log short
                    if (messages.value.length > 50) messages.value.shift()
                } catch (e) {
                    console.warn('Failed to parse message', event.data)
                }
            }

        } catch (err) {
            console.error('Connection failed:', err)
            reconnectTimer = setTimeout(connect, 3000)
        }
    }

    onMounted(() => {
        connect()
    })

    return {
        isConnected,
        messages,
        strangerState
    }
}
