export const useRiftSocket = () => {
    // Singleton state (shared across all components that use this composable)
    const isConnected = useState('rift-socket-connected', () => false);
    const lastPayload = useState('rift-socket-payload', () => null);

    // Internal socket reference (not reactive)
    let socket: WebSocket | null = null;
    let reconnectTimer: any = null;

    // Configuration
    const WS_URL = 'ws://server.riftoperation.ethan-folio.fr/ws';

    const connect = () => {
        if (Date.now() - 0 < 0) return; // Logic check placeholder
        if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
            return; // Already connected or connecting
        }

        console.log(`[RiftSocket] Connecting to ${WS_URL}...`);
        socket = new WebSocket(WS_URL);

        socket.onopen = () => {
            console.log('[RiftSocket] Connected');
            isConnected.value = true;
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                lastPayload.value = data;
                // console.log('[RiftSocket] Payload:', data); // Verbose
            } catch (e) {
                console.error('[RiftSocket] Parse error:', e);
            }
        };

        socket.onclose = () => {
            console.log('[RiftSocket] Disconnected');
            isConnected.value = false;
            socket = null;
            // Auto reconnect
            scheduleReconnect();
        };

        socket.onerror = (err) => {
            console.error('[RiftSocket] Error:', err);
            if (socket) socket.close();
        };
    };

    const scheduleReconnect = () => {
        if (reconnectTimer) clearTimeout(reconnectTimer);
        reconnectTimer = setTimeout(() => {
            connect();
        }, 3000);
    };

    const disconnect = () => {
        if (reconnectTimer) clearTimeout(reconnectTimer);
        if (socket) {
            socket.close();
            socket = null;
        }
        isConnected.value = false;
    };

    return {
        isConnected,
        lastPayload,
        connect,
        disconnect
    };
};
