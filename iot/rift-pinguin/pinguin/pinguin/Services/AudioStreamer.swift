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
        let inputNode = engine.inputNode
        let inputFormat = inputNode.inputFormat(forBus: 0)
        
        guard let targetFormat = AVAudioFormat(commonFormat: .pcmFormatFloat32, sampleRate: 24000, channels: 1, interleaved: false) else { 
            print("Failed to create target format")
            DispatchQueue.main.async { self.errorMessage = "Audio format error" }
            return 
        }
        
        guard let converter = AVAudioConverter(from: inputFormat, to: targetFormat) else {
            print("Failed to create converter")
            DispatchQueue.main.async { self.errorMessage = "Audio converter error" }
            return
        }
        
        inputNode.installTap(onBus: 0, bufferSize: 2048, format: inputFormat) { [weak self] (buffer, time) in
            guard let self = self else { return }
            
            let inputBlock: AVAudioConverterInputBlock = { inNumPackets, outStatus in
                outStatus.pointee = .haveData
                return buffer
            }
            
            let ratio = 24000.0 / inputFormat.sampleRate
            let capacity = AVAudioFrameCount(Double(buffer.frameLength) * ratio)
            
            if let outputBuffer = AVAudioPCMBuffer(pcmFormat: targetFormat, frameCapacity: capacity) {
                var error: NSError? = nil
                converter.convert(to: outputBuffer, error: &error, withInputFrom: inputBlock)
                
                if let error = error {
                    print("Conversion error: \(error)")
                    return
                }
                
                self.sendAudio(buffer: outputBuffer)
            }
        }
        
        do {
            try engine.start()
            DispatchQueue.main.async {
                self.isRecording = true
            }
        } catch {
            print("Engine start error: \(error)")
            DispatchQueue.main.async {
                self.errorMessage = "Could not start audio engine"
            }
        }
    }
    
    private func sendAudio(buffer: AVAudioPCMBuffer) {
        guard let floatChannelData = buffer.floatChannelData else { return }
        
        let frameLength = Int(buffer.frameLength)
        let dataSize = frameLength * MemoryLayout<Float>.size
        let data = Data(bytes: floatChannelData[0], count: dataSize)
        
        // Ensure socket is ready or simply send and handle error
        // Note: In robust app, we might want to check state
        let message = URLSessionWebSocketTask.Message.data(data)
        socket?.send(message) { error in
            if let error = error {
                print("Send error: \(error)")
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
