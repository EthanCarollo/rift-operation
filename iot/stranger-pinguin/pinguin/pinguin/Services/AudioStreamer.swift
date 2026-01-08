import Foundation
import AVFoundation
internal import Combine

class AudioStreamer: NSObject, ObservableObject, URLSessionWebSocketDelegate, AVAudioPlayerDelegate {
    @Published var transcribedText: String = ""
    @Published var latestAnswer: String = ""
    @Published var latestConfidence: Float = 0.0
    @Published var isRecording: Bool = false
    @Published var isConnected: Bool = false
    @Published var isServerHealthy: Bool = false
    @Published var errorMessage: String? = nil
    @Published var isPlayingAnswer: Bool = false
    @Published var serverMode: ServerMode = .cosmo {
        didSet {
            if oldValue != serverMode {
                reconnectToNewServer()
            }
        }
    }
    
    private var audioPlayer: AVPlayer?
    
    private var engine = AVAudioEngine()
    private var socket: URLSessionWebSocketTask?
    private var healthTimer: Timer?
    
    // Thread-safety for playback state
    private let audioLock = NSLock()
    private var _playbackActive: Bool = false
    
    // Thread-safety for audio setup (prevents race condition on double startAudioCapture)
    private let setupLock = NSLock()
    private var _isSettingUpAudio: Bool = false
    
    override init() {
        super.init()
    }
    
    convenience init(mode: ServerMode) {
        self.init()
        self.serverMode = mode
        startHealthCheck()
        connect()
    }
    
    func connect() {
        print("[AudioStreamer] Connecting to WebSocket (\(serverMode.displayName) mode)...")
        let url = AppConfig.websocketURL(for: serverMode)
        let session = URLSession(configuration: .default, delegate: self, delegateQueue: OperationQueue())
        socket = session.webSocketTask(with: url)
        socket?.resume()
        receiveMessage()
    }
    
    private func reconnectToNewServer() {
        print("[AudioStreamer] Switching to \(serverMode.displayName) mode...")
        // Stop recording if active
        if isRecording {
            stopAudioCapture()
        }
        // Close existing socket
        socket?.cancel(with: .normalClosure, reason: nil)
        DispatchQueue.main.async {
            self.isConnected = false
            self.transcribedText = ""
            self.latestAnswer = ""
        }
        // Reconnect to new server
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            self.connect()
            self.checkHealth()
        }
    }
    
    private func setPlaybackActive(_ active: Bool) {
        audioLock.lock()
        _playbackActive = active
        audioLock.unlock()
        print("[AudioStreamer] Playback state set to: \(active)")
    }
    
    deinit {
        healthTimer?.invalidate()
    }
    
    private func startHealthCheck() {
        healthTimer = Timer.scheduledTimer(withTimeInterval: 3.0, repeats: true) { [weak self] _ in
            self?.checkHealth()
        }
        checkHealth() // Initial check
    }
    
    private func checkHealth() {
        let url = AppConfig.httpURL(for: serverMode).appendingPathComponent("health")
        URLSession.shared.dataTask(with: url) { [weak self] _, response, error in
            let healthy = (error == nil && (response as? HTTPURLResponse)?.statusCode == 200)
            DispatchQueue.main.async {
                if self?.isServerHealthy != healthy {
                    self?.isServerHealthy = healthy
                    print("[AudioStreamer] Server health changed: \(healthy)")
                }
            }
        }.resume()
    }
    
    func startAudioCapture() {
        // Thread-safe check to prevent double setup
        setupLock.lock()
        if isRecording || _isSettingUpAudio {
            setupLock.unlock()
            print("[AudioStreamer] Already recording or setting up, ignoring startAudioCapture")
            return 
        }
        _isSettingUpAudio = true
        setupLock.unlock()
        
        print("[AudioStreamer] Starting audio capture...")
        setupAudio()
    }
    
    func stopAudioCapture() {
        if !isRecording { return }
        print("[AudioStreamer] Stopping audio capture...")
        engine.stop()
        engine.inputNode.removeTap(onBus: 0)
        // Do NOT close the socket here, we want to keep listening for state changes
        DispatchQueue.main.async {
            self.isRecording = false
        }
        
        // Reset setup flag
        setupLock.lock()
        _isSettingUpAudio = false
        setupLock.unlock()
        
        setPlaybackActive(false) // Safety reset
    }
    
    private func setupAudio() {
        print("[AudioStreamer] setupAudio() called")
        
        // Safety: Remove any existing tap before installing a new one
        // This prevents crash "required condition is false: nullptr == Tap()"
        engine.inputNode.removeTap(onBus: 0)
        
        // Also stop engine if it was running
        if engine.isRunning {
            engine.stop()
        }
        
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker, .allowBluetooth])
            // Set preferred sample rate and buffer for better compatibility with older devices
            try session.setPreferredSampleRate(48000)
            try session.setPreferredIOBufferDuration(0.1)
            try session.setActive(true)
            print("[AudioStreamer] Audio session configured for PlayAndRecord (Speaker/Bluetooth)")
            print("[AudioStreamer] Actual sample rate: \(session.sampleRate), IO buffer: \(session.ioBufferDuration)")
        } catch {
            print("[AudioStreamer] Failed to setup audio session: \(error)")
            DispatchQueue.main.async { self.errorMessage = "Audio session error: \(error.localizedDescription)" }
            
            // Reset setup flag on error
            setupLock.lock()
            _isSettingUpAudio = false
            setupLock.unlock()
            return
        }
        
        let inputNode = engine.inputNode
        let hardwareFormat = inputNode.inputFormat(forBus: 0)
        print("[AudioStreamer] Hardware format: \(hardwareFormat)")
        print("[AudioStreamer] Sample rate: \(hardwareFormat.sampleRate), channels: \(hardwareFormat.channelCount)")
        
        // Check for valid format (prevent 0Hz error)
        if hardwareFormat.sampleRate == 0 {
            print("[AudioStreamer] ERROR: Invalid input format: 0Hz - microphone not available?")
            DispatchQueue.main.async { self.errorMessage = "Microphone not available" }
            return
        }
        
        // Target: 24kHz, 1 channel, Float32 - what the server expects
        guard let targetFormat = AVAudioFormat(commonFormat: .pcmFormatFloat32, sampleRate: 24000, channels: 1, interleaved: false) else {
            print("[AudioStreamer] ERROR: Failed to create target format")
            DispatchQueue.main.async { self.errorMessage = "Audio format error" }
            return
        }
        print("[AudioStreamer] Target format: \(targetFormat)")
        
        // Install tap with the HARDWARE format (what the mic provides)
        // Then convert manually using a properly configured converter
        guard let converter = AVAudioConverter(from: hardwareFormat, to: targetFormat) else {
            print("[AudioStreamer] ERROR: Failed to create converter")
            DispatchQueue.main.async { self.errorMessage = "Audio converter error" }
            return
        }
        print("[AudioStreamer] Converter created successfully")
        
        print("[AudioStreamer] Installing tap on input node with hardware format...")
        // Use hardware format for tap - this is the key fix!
        inputNode.installTap(onBus: 0, bufferSize: 4800, format: hardwareFormat) { [weak self] (buffer, time) in
            guard let self = self else {
                print("[AudioStreamer] TAP: self is nil, returning")
                return
            }
            
            // Calculate output frame count based on sample rate ratio
            let ratio = targetFormat.sampleRate / hardwareFormat.sampleRate
            let outputFrameCapacity = AVAudioFrameCount(Double(buffer.frameLength) * ratio)
            
            guard let outputBuffer = AVAudioPCMBuffer(pcmFormat: targetFormat, frameCapacity: outputFrameCapacity) else {
                print("[AudioStreamer] Failed to create output buffer")
                return
            }
            
            var error: NSError?
            
            // Use simple convert method for non-VBR formats
            let inputBlock: AVAudioConverterInputBlock = { inNumPackets, outStatus in
                outStatus.pointee = .haveData
                return buffer
            }
            
            let status = converter.convert(to: outputBuffer, error: &error, withInputFrom: inputBlock)
            
            if let error = error {
                print("[AudioStreamer] Conversion error: \(error)")
                return
            }
            
            if status == .error {
                print("[AudioStreamer] Conversion status: error")
                return
            }
            
            // Only send if we have frames AND we are not playing back
            if outputBuffer.frameLength > 0 {
                // Thread-safe check
                var shouldSend = true
                self.audioLock.lock()
                if self._playbackActive {
                    shouldSend = false
                }
                self.audioLock.unlock()
                
                if shouldSend {
                    self.sendAudio(buffer: outputBuffer)
                }
            }
        }
        print("[AudioStreamer] Tap installed")
        
        do {
            try engine.start()
            print("[AudioStreamer] Engine started successfully!")
            
            // Reset setup flag AFTER engine starts
            setupLock.lock()
            _isSettingUpAudio = false
            setupLock.unlock()
            
            DispatchQueue.main.async {
                self.isRecording = true
            }
        } catch {
            print("[AudioStreamer] ERROR: Engine start error: \(error)")
            // Reset setup flag on error too
            setupLock.lock()
            _isSettingUpAudio = false
            setupLock.unlock()
            DispatchQueue.main.async {
                self.errorMessage = "Could not start audio engine"
            }
        }
    }
    
    private var sendCount = 0
    
    private func sendAudio(buffer: AVAudioPCMBuffer) {
        // Check if socket exists and we're connected
        guard let socket = socket, isConnected else {
            if sendCount <= 5 || sendCount % 100 == 0 {
                print("[AudioStreamer] Cannot send: socket=\(socket != nil), connected=\(isConnected)")
            }
            sendCount += 1
            return
        }
        
        guard let floatChannelData = buffer.floatChannelData else {
            print("[AudioStreamer] No float channel data!")
            return
        }
        
        let frameLength = Int(buffer.frameLength)
        if frameLength == 0 {
            print("[AudioStreamer] Warning: buffer has 0 frames")
            return
        }
        
        let dataSize = frameLength * MemoryLayout<Float>.size
        let data = Data(bytes: floatChannelData[0], count: dataSize)
        
        sendCount += 1
        if sendCount <= 5 || sendCount % 50 == 0 {
            print("[AudioStreamer] Sending chunk #\(sendCount): \(data.count) bytes, \(frameLength) samples")
        }
        

        
        // Final gate check (redundant but safe)
        self.audioLock.lock()
        let currentlyPlaying = self._playbackActive
        self.audioLock.unlock()
        
        if currentlyPlaying { return }
        
        let message = URLSessionWebSocketTask.Message.data(data)
        socket.send(message) { error in
            if let error = error {
                print("[AudioStreamer] Send error: \(error)")
            }
        }
    }
    
    private func receiveMessage() {
        socket?.receive { [weak self] result in
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    if text.starts(with: "stt: ") {
                        let content = String(text.dropFirst(5))
                        DispatchQueue.main.async {
                            self?.transcribedText += content
                        }
                    } else if let data = text.data(using: .utf8),
                              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                        
                        if let type = json["type"] as? String {
                            if type == "stranger_state", let state = json["state"] as? String {
                                print("[AudioStreamer] Received STATE command: \(state)")
                                if state == "active" {
                                    self?.startAudioCapture()
                                } else if state == "inactive" {
                                    self?.stopAudioCapture()
                                }
                            } else if type == "qa_answer", let answer = json["answer"] as? String {
                                DispatchQueue.main.async {
                                    self?.latestAnswer = answer
                                    self?.latestConfidence = Float(json["confidence"] as? Double ?? 0.0)
                                    print("[AudioStreamer] Received QA Answer: \(answer) (conf: \(self?.latestConfidence ?? 0))")
                                    
                                    // Handle Audio Playback (Base64)
                                    if let audioBase64 = json["audio_base64"] as? String,
                                       let audioData = Data(base64Encoded: audioBase64) {
                                        let filename = json["audio_file"] as? String ?? "unknown"
                                        self?.playAudioData(data: audioData, filename: filename)
                                    }
                                }
                            } else if type == "dark_cosmo_detected" {
                                print("[AudioStreamer] 🌙 Dark Cosmo detected! Playing notification audio...")
                                DispatchQueue.main.async {
                                    // Handle Audio Playback (Base64)
                                    if let audioBase64 = json["audio_base64"] as? String,
                                       let audioData = Data(base64Encoded: audioBase64) {
                                        let filename = json["audio_file"] as? String ?? "dark_cosmo_audio"
                                        self?.playAudioData(data: audioData, filename: filename)
                                    }
                                }
                            } else if type == "system_error" {
                                DispatchQueue.main.async {
                                    self?.errorMessage = json["message"] as? String
                                }
                            }
                        }
                    } else {
                        // Fallback/Legacy
                        DispatchQueue.main.async {
                            self?.transcribedText += text
                        }
                    }
                case .data(_):
                    break
                @unknown default:
                    break
                }
                self?.receiveMessage()
            case .failure(let error):
                print("[AudioStreamer] Receive error: \(error)")
                DispatchQueue.main.async {
                    self?.isConnected = false
                }
            }
        }
    }
    
    private var audioPlayerFn: AVAudioPlayer?
    
    private func playAudioData(data: Data, filename: String) {
        do {
            print("🔊 [MOBILE] STARTING AUDIO PLAYBACK: \(filename) (\(data.count) bytes) 🔊")
            
            // SYNCHRONOUSLY lock out recording before we even touch the player
            setPlaybackActive(true)
            
            audioPlayerFn = try AVAudioPlayer(data: data)
            audioPlayerFn?.delegate = self
            audioPlayerFn?.prepareToPlay()
            
            DispatchQueue.main.async {
                self.isPlayingAnswer = true
            }
            
            audioPlayerFn?.play()
        } catch {
            print("❌ [AudioStreamer] Failed to play audio data: \(error)")
            setPlaybackActive(false) // Safety reset
            DispatchQueue.main.async {
                self.isPlayingAnswer = false
            }
        }
    }
    
    // MARK: - AVAudioPlayerDelegate
    
    func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        print("🔈 [MOBILE] AUDIO PLAYBACK FINISHED (Success: \(flag)) 🔈")
        
        setPlaybackActive(false)
        
        DispatchQueue.main.async {
            self.isPlayingAnswer = false
        }
    }
    
    func audioPlayerDecodeErrorDidOccur(_ player: AVAudioPlayer, error: Error?) {
        print("❌ [MOBILE] AUDIO DECODE ERROR: \(String(describing: error))")
        
        setPlaybackActive(false)
        
        DispatchQueue.main.async {
            self.isPlayingAnswer = false
        }
    }
    
    // MARK: - URLSessionWebSocketDelegate
    
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didOpenWithProtocol protocol: String?) {
        print("[AudioStreamer] WebSocket connected")
        DispatchQueue.main.async {
            self.isConnected = true
        }
    }
    
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didCloseWith closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) {
        print("[AudioStreamer] WebSocket disconnected")
        DispatchQueue.main.async {
            self.isConnected = false
        }
    }
}
