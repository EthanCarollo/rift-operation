package com.example.test_application_operateur

import android.content.Context
import android.util.Log
import io.livekit.android.LiveKit
import io.livekit.android.events.RoomEvent
import io.livekit.android.events.collect
import io.livekit.android.room.Room
import io.livekit.android.room.participant.Participant
import io.livekit.android.room.participant.RemoteParticipant
import io.livekit.android.room.track.LocalAudioTrack
import io.livekit.android.room.track.Track
import io.livekit.android.room.track.RemoteTrackPublication
import io.livekit.android.room.track.DataPublishReliability
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay

/**
 * LiveKitManager - Multi-Room Implementation
 * 
 * Architecture:
 * - Room "walkie-A": Dedicated to Operator <-> Client A
 * - Room "walkie-C": Dedicated to Operator <-> Client C
 * 
 * Connections:
 * - Client A: Connects ONLY to "walkie-A"
 * - Client C: Connects ONLY to "walkie-C"
 * - Operator B: Connects to BOTH "walkie-A" and "walkie-C"
 * 
 * Audio Routing:
 * - Reception: Operator B hears audio from both rooms (mixed).
 * - Transmission: Operator B toggles Microphone between Room A and Room C.
 */
class LiveKitManager(private val context: Context) {
    
    companion object {
        private const val TAG = "LiveKit"
        private const val BASE_ROOM_NAME = "walkie" // will append -A or -C
        
        private const val API_KEY = "devkey123456789012345678901234"
        private const val API_SECRET = "secretkey1234567890123456789012"
    }
    
    enum class Role { OPERATOR_B, CLIENT_A, CLIENT_C }
    enum class Channel { NONE, LEFT, RIGHT }
    
    var role = Role.OPERATOR_B
    var serverUrl = "ws://192.168.10.4:7880"
    
    @Volatile var currentChannel = Channel.NONE
    
    // We may need up to 2 rooms (for Operator)
    private var roomA: Room? = null
    private var roomC: Room? = null
    
    private var scope: CoroutineScope? = null
    
    // Callbacks
    var onStatus: ((String) -> Unit)? = null
    var onMicLevel: ((Int) -> Unit)? = null
    var onRemoteLevel: ((Int) -> Unit)? = null
    var onParticipantJoined: ((String) -> Unit)? = null // Simplification: just notifies connect
    
    private fun configureAudio() {
        try {
            val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as android.media.AudioManager
            
            // "Jolting" the audio stack: older Samsungs sometimes need a mode switch to wake up the routing
            audioManager.mode = android.media.AudioManager.MODE_NORMAL
            
            if (!audioManager.isSpeakerphoneOn) {
                audioManager.isSpeakerphoneOn = true
            }
            
            audioManager.mode = android.media.AudioManager.MODE_IN_COMMUNICATION
            
            Log.d(TAG, "🔊 Audio Configured: Force Speaker + Mode IN_COMMUNICATION")
        } catch (e: Exception) {
            Log.e(TAG, "Audio config error", e)
        }
    }

    // Aggressive loop to fight OS/Library resetting the audio route
    private fun monitorAudioSettings() {
        scope?.launch {
            while (roomA?.state == Room.State.CONNECTED || roomC?.state == Room.State.CONNECTED) {
                try {
                    val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as android.media.AudioManager
                    if (!audioManager.isSpeakerphoneOn) {
                        Log.w(TAG, "🔊 Detected Speaker OFF - Forcing ON")
                        audioManager.isSpeakerphoneOn = true
                    }
                    if (audioManager.mode != android.media.AudioManager.MODE_IN_COMMUNICATION) {
                        // Only force if strictly necessary, changing mode can cause glitches
                         audioManager.mode = android.media.AudioManager.MODE_IN_COMMUNICATION
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Audio monitor error", e)
                }
                delay(2000) // Check every 2 seconds
            }
        }
    }
    
    fun connect(): Boolean {
        Log.d(TAG, "=== CONNEXION LiveKit (Multi-Room) ===")
        Log.d(TAG, "Role: $role")
        
        scope = CoroutineScope(Dispatchers.Main + Job())
        
        scope?.launch {
            try {
                // Use default options (AutoSubscribe=true, etc.)
                // Multi-Room isolation makes AutoSubscribe safe/desirable.
                
                // Re-enforce audio config
                configureAudio()
                
                when (role) {
                    Role.CLIENT_A -> {
                        connectToRoom("walkie-A", "A") { r -> roomA = r }
                    }
                    Role.CLIENT_C -> {
                        connectToRoom("walkie-C", "C") { r -> roomC = r }
                    }
                    Role.OPERATOR_B -> {
                        // Operator connects to BOTH
                        // Assign Identity "B" to both connections (LiveKit allows same identity in diff rooms)
                        onStatus?.invoke("🔄 Connexion Room A...")
                        connectToRoom("walkie-A", "B") { r -> roomA = r }
                        
                        delay(500) // Small delay to separate connection logic
                        
                        onStatus?.invoke("🔄 Connexion Room C...")
                        connectToRoom("walkie-C", "B") { r -> roomC = r }
                        
                        onStatus?.invoke("🟢 Connecté (A + C)")
                    }
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Global connection error", e)
                onStatus?.invoke("❌ Erreur: ${e.message}")
            }
        }
        return true
    }
    
    private suspend fun connectToRoom(
        roomName: String, 
        identity: String, 
        onRoomCreated: (Room) -> Unit
    ) {
        val room = LiveKit.create(context) // Default options
        onRoomCreated(room)
        
        // Listeners must be attached before connect
        listenToRoomEvents(room, roomName)
        
        val token = generateToken(identity, roomName)
        Log.d(TAG, "Connecting to $roomName as $identity...")
        
        room.connect(serverUrl, token) // Default options
        Log.d(TAG, "✅ Connected to $roomName")
        
        // Default Mic State:
        // Clients A/C: Always ON (Monitoring style) - or PTT if desired?
        // User requested: "Quand A parle, seulement B entend". typically implies Open Mic or PTT on Client.
        // Assuming Clients have Open Mic for now as per previous logic, OR we can default to ON.
        // For B: Default OFF.
        
        if (identity == "A" || identity == "C") {
            room.localParticipant.setMicrophoneEnabled(true)
        } else {
            // Operator B starts muted
            room.localParticipant.setMicrophoneEnabled(false)
        }
        
        if (role != Role.OPERATOR_B) {
            onStatus?.invoke("🟢 Connecté ($roomName)")
        }
    }
    
    private fun listenToRoomEvents(room: Room, roomName: String) {
        scope?.launch {
            room.events.collect { event ->
                when (event) {
                    is RoomEvent.ParticipantConnected -> {
                        Log.d(TAG, "[$roomName] +Participant: ${event.participant.identity?.value}")
                        if (role == Role.OPERATOR_B) {
                            onParticipantJoined?.invoke("${event.participant.identity?.value}")
                        }
                    }
                    is RoomEvent.ParticipantDisconnected -> {
                        Log.d(TAG, "[$roomName] -Participant: ${event.participant.identity?.value}")
                    }
                    is RoomEvent.ActiveSpeakersChanged -> {
                        val speakers = event.speakers
                        if (speakers.isNotEmpty()) {
                            // Simple visual feedback
                            onRemoteLevel?.invoke(50)
                            Log.v(TAG, "[$roomName] Speaking: ${speakers.map { it.identity?.value }}")
                        } else {
                            onRemoteLevel?.invoke(0)
                        }
                    }
                    is RoomEvent.Disconnected -> {
                        Log.d(TAG, "[$roomName] Disconnected")
                    }
                    else -> {}
                }
            }
        }
    }
    
    fun setChannel(channel: Channel) {
        currentChannel = channel
        
        // This is only for Operator B
        if (role == Role.OPERATOR_B) {
            val rA = roomA
            val rC = roomC
            
            scope?.launch {
                try {
                    when (channel) {
                        Channel.LEFT -> {
                            // Talk to A
                            Log.d(TAG, "Mic: A=ON, C=OFF")
                            rC?.localParticipant?.setMicrophoneEnabled(false)
                            delay(50) // Short buffer for HW switch
                            rA?.localParticipant?.setMicrophoneEnabled(true)
                        }
                        Channel.RIGHT -> {
                            // Talk to C
                            Log.d(TAG, "Mic: A=OFF, C=ON")
                            rA?.localParticipant?.setMicrophoneEnabled(false)
                            delay(50)
                            rC?.localParticipant?.setMicrophoneEnabled(true)
                        }
                        Channel.NONE -> {
                            // Mute all
                            Log.d(TAG, "Mic: A=OFF, C=OFF")
                            rA?.localParticipant?.setMicrophoneEnabled(false)
                            rC?.localParticipant?.setMicrophoneEnabled(false)
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error switching mic", e)
                }
            }
        }
    }
    
    fun disconnect() {
        Log.d(TAG, "=== DÉCONNEXION ===")
        scope?.launch {
            roomA?.disconnect()
            roomA?.release()
            
            roomC?.disconnect()
            roomC?.release()
        }
        scope?.cancel()
        
        roomA = null
        roomC = null
        onStatus?.invoke("⏹️ Déconnecté")
    }
    
    private fun generateToken(identity: String, roomName: String): String {
        return createSimpleToken(identity, roomName)
    }
    
    private fun createSimpleToken(identity: String, roomName: String): String {
        val header = android.util.Base64.encodeToString(
            """{"alg":"HS256","typ":"JWT"}""".toByteArray(),
            android.util.Base64.URL_SAFE or android.util.Base64.NO_WRAP or android.util.Base64.NO_PADDING
        )
        
        val exp = (System.currentTimeMillis() / 1000) + 86400 // 24 hours
        val payload = android.util.Base64.encodeToString(
            """{"iss":"$API_KEY","sub":"$identity","name":"$identity","video":{"room":"$roomName","roomJoin":true},"exp":$exp}""".toByteArray(),
            android.util.Base64.URL_SAFE or android.util.Base64.NO_WRAP or android.util.Base64.NO_PADDING
        )
        
        val signatureInput = "$header.$payload"
        val mac = javax.crypto.Mac.getInstance("HmacSHA256")
        mac.init(javax.crypto.spec.SecretKeySpec(API_SECRET.toByteArray(), "HmacSHA256"))
        val signature = android.util.Base64.encodeToString(
            mac.doFinal(signatureInput.toByteArray()),
            android.util.Base64.URL_SAFE or android.util.Base64.NO_WRAP or android.util.Base64.NO_PADDING
        )
        
        return "$header.$payload.$signature"
    }
}
