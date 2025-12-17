import Foundation
import AVFoundation
internal import Combine

class AudioStreamer: NSObject, ObservableObject, URLSessionWebSocketDelegate {
    @Published var transcribedText: String = ""
    @Published var isRecording: Bool = false
    @Published var errorMessage: String? = nil
    
    private var engine = AVAudioEngine()
    private var socket: URLSessionWebSocketTask?
    
    func startRecording() {
        let url = AppConfig.websocketURL
        let session = URLSession(configuration: .default, delegate: self, delegateQueue: OperationQueue())
        socket = session.webSocketTask(with: url)
        socket?.resume()
        receiveMessage()
        
        setupAudio()
    }
    
    func stopRecording() {
        engine.stop()
        engine.inputNode.removeTap(onBus: 0)
        socket?.cancel(with: .normalClosure, reason: nil)
        isRecording = false
    }
    
    private func setupAudio() {
        print("[AudioStreamer] setupAudio() called")
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.playAndRecord, mode: .measurement, options: .duckOthers)
            try session.setActive(true)
            print("[AudioStreamer] Audio session configured successfully")
        } catch {
            print("[AudioStreamer] Failed to setup audio session: \(error)")
            DispatchQueue.main.async { self.errorMessage = "Audio session error: \(error.localizedDescription)" }
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
            guard let self = self else { return }
            
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
            
            // Only send if we have frames
            if outputBuffer.frameLength > 0 {
                self.sendAudio(buffer: outputBuffer)
            }
        }
        print("[AudioStreamer] Tap installed")
        
        do {
            try engine.start()
            print("[AudioStreamer] Engine started successfully!")
            DispatchQueue.main.async {
                self.isRecording = true
            }
        } catch {
            print("[AudioStreamer] ERROR: Engine start error: \(error)")
            DispatchQueue.main.async {
                self.errorMessage = "Could not start audio engine"
            }
        }
    }
    
    private var sendCount = 0
    
    private func sendAudio(buffer: AVAudioPCMBuffer) {
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
        
        let message = URLSessionWebSocketTask.Message.data(data)
        socket?.send(message) { error in
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
                    DispatchQueue.main.async {
                        self?.transcribedText += text
                    }
                case .data(_):
                    break
                @unknown default:
                    break
                }
                self?.receiveMessage()
            case .failure(let error):
                print("Receive error: \(error)")
            }
        }
    }
}
