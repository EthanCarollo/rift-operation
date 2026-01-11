export const useStrangerSocket = () => {
    const config = useRuntimeConfig()
    const isConnected = useState<boolean>('socket-connected', () => false)
    const messages = useState<any[]>('socket-messages', () => [])
    const strangerState = useState<string>('stranger-state', () => 'inactive')
    const wsUrl = useState<string>('ws-url', () => config.public.defaultWsUrl as string)
    let socket: WebSocket | null = null
    let reconnectTimer: any = null

    const connect = () => {
        if (socket?.readyState === WebSocket.OPEN) return

        try {
            socket = new WebSocket(wsUrl.value)

            socket.onopen = () => {
                console.log('WebSocket Connected to', wsUrl.value)
                isConnected.value = true
                if (reconnectTimer) {
                    clearTimeout(reconnectTimer)
                    reconnectTimer = null
                }
                // Send presence message to websocket panel
                socket?.send(JSON.stringify({
                    device_id: 'StrangerDreamInstruction'
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

    const disconnect = () => {
        if (reconnectTimer) {
            clearTimeout(reconnectTimer)
            reconnectTimer = null
        }
        if (socket) {
            socket.close()
            socket = null
        }
        isConnected.value = false
    }

    const reconnectWithUrl = (newUrl: string) => {
        wsUrl.value = newUrl
        disconnect()
        connect()
    }

    onMounted(() => {
        connect()
    })

    return {
        isConnected,
        messages,
        strangerState,
        wsUrl,
        reconnectWithUrl,
        disconnect
    }
}

