
import { io, Socket } from 'socket.io-client';

// Global singleton to reuse connection
let globalSocket: Socket | null = null;

export const useRiftSocket = () => {
    const config = useRuntimeConfig();
    const SOCKET_URL = (config.public.backendUrl as string) || 'http://localhost:5010';

    const isConnected = useState<boolean>('rift-socket-connected', () => false);
    const lastPayload = useState<any>('rift-socket-payload', () => null);

    const connect = () => {
        if (globalSocket && globalSocket.connected) {
            isConnected.value = true;
            return;
        }

        console.log(`[BattleSocket] Connecting to Local Backend @ ${SOCKET_URL}...`);
        
        globalSocket = io(SOCKET_URL, {
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionAttempts: Infinity,
            reconnectionDelay: 1000,
        });

        globalSocket.on('connect', () => {
            console.log('[BattleSocket] Connected to Backend');
            isConnected.value = true;
        });

        globalSocket.on('disconnect', () => {
            console.log('[BattleSocket] Disconnected from Backend');
            isConnected.value = false;
        });

        // Backend acts as a proxy, forwarding Rift events as 'rift_state_update'
        // or potentially broadcasting 'status' which contains everything.
        // Let's listen for 'status' as it's what BattleService emits currently.
        globalSocket.on('status', (data: any) => {
            // BattleService emits 'status' with local state + ws_state (Rift State)
            if (data && data.ws_state) {
                // Determine if we should use the raw ws_state (Rift payload) 
                // or if we need to map it. 
                // The existing code expects the Raw Rift Payload structure.
                lastPayload.value = data.ws_state;
            }
        });

        // Also listen for direct 'rift_proxy_message' if we add that later
        globalSocket.on('rift_proxy_message', (data: any) => {
             lastPayload.value = data;
        });
    };

    const disconnect = () => {
        if (globalSocket) {
            globalSocket.disconnect();
            globalSocket = null;
        }
        isConnected.value = false;
    };

    const send = (payload: any) => {
        if (globalSocket && isConnected.value) {
            console.log('[BattleSocket] Proxying payload to Rift via Backend:', payload);
            // new event 'proxy_to_rift' that BattleWebServer will handle
            globalSocket.emit('proxy_to_rift', payload);
        } else {
            console.warn('[BattleSocket] Not connected, cannot send:', payload);
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
