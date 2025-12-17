//
//  ContentView.swift
//  pinguin
//
//  Created by eth on 17/12/2025.
//

import SwiftUI
import AVFoundation

class AudioStreamer: NSObject, ObservableObject, URLSessionWebSocketDelegate {
    @Published var transcribedText: String = ""
    @Published var isRecording: Bool = false
    @Published var errorMessage: String? = nil
    
    private var engine = AVAudioEngine()
    private var socket: URLSessionWebSocketTask?
    
    func startRecording() {
        // WebSocket Setup
        // Check if using simulator or device. If device, localhost won't work.
        // Ideally, user should configure this. Defaulting to localhost for simulator.
        let url = URL(string: "ws://localhost:8000/ws")!
        let session = URLSession(configuration: .default, delegate: self, delegateQueue: OperationQueue())
        socket = session.webSocketTask(with: url)
        socket?.resume()
        receiveMessage()
        
        // Audio Setup
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
        
        // Target: 24kHz, 1 channel, Float32
        guard let targetFormat = AVAudioFormat(commonFormat: .pcmFormatFloat32, sampleRate: 24000, channels: 1, interleaved: false) else { 
            print("Failed to create target format")
            return 
        }
        
        guard let converter = AVAudioConverter(from: inputFormat, to: targetFormat) else {
            print("Failed to create converter")
            return
        }
        
        inputNode.installTap(onBus: 0, bufferSize: 2048, format: inputFormat) { [weak self] (buffer, time) in
            guard let self = self else { return }
            
            // Conversion
            let inputBlock: AVAudioConverterInputBlock = { inNumPackets, outStatus in
                outStatus.pointee = .haveData
                return buffer
            }
            
            // Calculate output buffer size
            // Ratio = 24000 / InputSampleRate
            let ratio = 24000.0 / inputFormat.sampleRate
            let capacity = AVAudioFrameCount(Double(buffer.frameLength) * ratio)
            
            if let outputBuffer = AVAudioPCMBuffer(pcmFormat: targetFormat, frameCapacity: capacity) {
                var error: NSError? = nil
                converter.convert(to: outputBuffer, error: &error, withInputFrom: inputBlock)
                
                if let error = error {
                    print("Conversion error: \(error)")
                    return
                }
                
                // Send data
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
                self?.receiveMessage() // Keep listening
            case .failure(let error):
                print("Receive error: \(error)")
                // Reconnect logic could go here
            }
        }
    }
}

struct ContentView: View {
    @StateObject private var streamer = AudioStreamer()
    
    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            
            VStack(spacing: 40) {
                // Header / Title
                Text("RIFT OPERATION")
                    .font(.system(size: 14, weight: .medium, design: .monospaced))
                    .tracking(2)
                    .foregroundStyle(.white.opacity(0.8))
                    .padding(.top, 40)
                                
                // Transcription Area
                ScrollView {
                    Text(streamer.transcribedText.isEmpty ? "Transcription will appear here..." : streamer.transcribedText)
                        .font(.system(size: 24, weight: .light, design: .default))
                        .foregroundStyle(.white)
                        .multilineTextAlignment(.leading)
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .animation(.default, value: streamer.transcribedText)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(
                    RoundedRectangle(cornerRadius: 20)
                        .fill(Color.white.opacity(0.05))
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 20)
                        .stroke(Color.white.opacity(0.1), lineWidth: 1)
                )
                .padding(.horizontal)
                
                // Controls
                Button(action: {
                    if streamer.isRecording {
                        streamer.stopRecording()
                    } else {
                        streamer.startRecording()
                    }
                }) {
                    ZStack {
                        Circle()
                            .stroke(Color.white.opacity(0.2), lineWidth: 1)
                            .frame(width: 80, height: 80)
                        
                        Circle()
                            .fill(streamer.isRecording ? Color.red : Color.white)
                            .frame(width: 60, height: 60)
                            .overlay(
                                Circle()
                                    .stroke(Color.black, lineWidth: 2)
                                    .opacity(streamer.isRecording ? 0 : 1)
                            )
                        
                        if streamer.isRecording {
                            RoundedRectangle(cornerRadius: 4)
                                .fill(Color.white)
                                .frame(width: 24, height: 24)
                        }
                    }
                }
                .padding(.bottom, 40)
                
                if let error = streamer.errorMessage {
                    Text(error)
                        .font(.caption)
                        .foregroundStyle(.red)
                        .padding()
                }
            }
        }
        .preferredColorScheme(.dark)
    }
}

#Preview {
    ContentView()
}
