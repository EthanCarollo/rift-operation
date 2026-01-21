
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
            // Priority: Use local backend's battle_state for responsiveness,
            // fall back to ws_state from Rift server
            if (data) {
                const payload: any = {};
                
                // Always use local backend state if available (faster, more responsive)
                if (data.battle_state) {
                    payload.battle_state = data.battle_state;
                }
                if (data.current_hp !== undefined) {
                    payload.battle_boss_hp = data.current_hp;
                }
                if (data.current_attack !== undefined) {
                    payload.battle_boss_attack = data.current_attack;
                }
                
                // Merge with Rift state if available (for other fields)
                if (data.ws_state) {
                    // Rift state provides additional fields, but local state takes priority
                    lastPayload.value = { ...data.ws_state, ...payload };
                } else if (Object.keys(payload).length > 0) {
                    // Only local state available
                    lastPayload.value = { ...lastPayload.value, ...payload };
                }
            }
        });

        // Listen for explicit battle state updates from backend (force_start_fight, etc.)
        globalSocket.on('battle_state_update', (data: any) => {
            if (data) {
                console.log('[BattleSocket] Received battle_state_update:', data);
                lastPayload.value = { ...lastPayload.value, ...data };
            }
        });

        // Listen for direct image updates from BattleService (FightingState)
        // This is critical for real-time validation feedback and clearing images
        globalSocket.on('battle_image_update', (data: any) => {
             if (data && data.role) {
                 // Map to payload format expected by useBattleState
                 const key = data.role === 'nightmare' 
                     ? 'battle_drawing_nightmare_image' 
                     : 'battle_drawing_dream_image';
                 
                 // Update lastPayload with the new image (or null)
                 lastPayload.value = {
                     ...lastPayload.value,
                     [key]: data.image
                 };
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
