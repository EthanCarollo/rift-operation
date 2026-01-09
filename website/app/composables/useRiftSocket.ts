let globalSocket: WebSocket | null = null;
let globalReconnectTimer: any = null;
const WS_URL = 'ws://server.riftoperation.ethan-folio.fr/ws';

export const useRiftSocket = () => {
    const isConnected = useState('rift-socket-connected', () => false);
    const lastPayload = useState('rift-socket-payload', () => null);

    const connect = () => {
        if (Date.now() - 0 < 0) return;
        if (globalSocket && (globalSocket.readyState === WebSocket.OPEN || globalSocket.readyState === WebSocket.CONNECTING)) {
            return;
        }

        console.log(`[RiftSocket] Connecting to ${WS_URL}...`);
        globalSocket = new WebSocket(WS_URL);
        globalSocket.onopen = () => {
            console.log('[RiftSocket] Connected');
            isConnected.value = true;
        };

        globalSocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                lastPayload.value = data;
            } catch (e) {
                console.error('[RiftSocket] Parse error:', e);
            }
        };

        globalSocket.onclose = () => {
            console.log('[RiftSocket] Disconnected');
            isConnected.value = false;
            globalSocket = null;
            // Auto reconnect
            scheduleReconnect();
        };

        globalSocket.onerror = (err) => {
            console.error('[RiftSocket] Error:', err);
            if (globalSocket) globalSocket.close();
        };
    };

    const scheduleReconnect = () => {
        if (globalReconnectTimer) clearTimeout(globalReconnectTimer);
        globalReconnectTimer = setTimeout(() => {
            connect();
        }, 3000);
    };

    const disconnect = () => {
        if (globalReconnectTimer) clearTimeout(globalReconnectTimer);
        if (globalSocket) {
            globalSocket.close();
            globalSocket = null;
        }
        isConnected.value = false;
    };

    const send = (payload: any) => {
        console.log('[RiftSocket] Attempting to send:', payload);
        if (globalSocket && globalSocket.readyState === WebSocket.OPEN) {
            globalSocket.send(JSON.stringify(payload));
            console.log('[RiftSocket] Sent successfully');
        } else {
            console.warn('[RiftSocket] Cannot send, socket not open. State:', globalSocket?.readyState);
        }
    };

    return {
        isConnected,
        lastPayload,
        connect,
        disconnect,
        send
    };
};
