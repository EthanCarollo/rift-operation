//
//  ContentView.swift
//  pinguin
//
//  Created by eth on 17/12/2025.
//

import SwiftUI

struct ContentView: View {
    @StateObject private var streamer = AudioStreamer()
    
    var body: some View {
        ZStack {
            // Background with subtle ceramic tint
            Color(hex: "F8F8F8").ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Persistent Top Status Bar
                HStack {
                    HStack(spacing: 12) {
                        StatusIndicator(
                            isHealthy: streamer.isServerHealthy,
                            isConnected: streamer.isConnected
                        )
                        
                        VStack(alignment: .leading, spacing: 2) {
                            Text(streamer.isServerHealthy ? (streamer.isConnected ? "SYSTEM ACTIVE" : "STANDBY") : "OFFLINE")
                                .font(.system(size: 10, weight: .bold, design: .monospaced))
                                .foregroundStyle(streamer.isServerHealthy ? (streamer.isConnected ? .green : .orange) : .red)
                            
                            Text(AppConfig.serverHost)
                                .font(.system(size: 9, design: .monospaced))
                                .foregroundStyle(.gray.opacity(0.6))
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(.white)
                            .shadow(color: .black.opacity(0.03), radius: 5, x: 0, y: 2)
                    )
                    
                    Spacer()
                    
                    // Waveform Activity (Visual only)
                    if streamer.isRecording {
                        HStack(spacing: 3) {
                            ForEach(0..<4) { i in
                                Capsule()
                                    .fill(Color.black.opacity(0.1))
                                    .frame(width: 2, height: 12)
                                    .scaleEffect(y: streamer.isRecording ? 1.5 : 1.0)
                                    .animation(.easeInOut(duration: 0.5).repeatForever().delay(Double(i) * 0.1), value: streamer.isRecording)
                            }
                        }
                    }
                }
                .padding(.horizontal, 24)
                .padding(.top, 12)
                
                VStack(spacing: 24) {
                    HeaderView()
                        .padding(.top, 20)
                    
                    // Knowledge / QA Section (Floating Card)
                    ZStack {
                        if !streamer.latestAnswer.isEmpty {
                            VStack(alignment: .leading, spacing: 14) {
                                HStack {
                                    Image(systemName: "sparkles")
                                        .font(.system(size: 14, weight: .semibold))
                                        .foregroundStyle(.blue)
                                    Text("RÉPONSE DU PINGUIN")
                                        .font(.system(size: 11, weight: .black))
                                        .foregroundStyle(.blue.opacity(0.8))
                                        .tracking(1.5)
                                }
                                
                                Text(streamer.latestAnswer)
                                    .font(.system(size: 19, weight: .medium, design: .serif))
                                    .foregroundStyle(.black.opacity(0.9))
                                    .lineSpacing(6)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                            .padding(24)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(
                                RoundedRectangle(cornerRadius: 32)
                                    .fill(.white)
                                    .shadow(color: .black.opacity(0.06), radius: 20, x: 0, y: 10)
                            )
                            .padding(.horizontal, 24)
                            .transition(.asymmetric(
                                insertion: .move(edge: .top).combined(with: .opacity),
                                removal: .opacity.combined(with: .scale(scale: 0.9))
                            ))
                        }
                    }
                    .animation(.spring(response: 0.6, dampingFraction: 0.8), value: streamer.latestAnswer)
                    
                    // Main Transcription Area
                    LogView(text: streamer.transcribedText)
                        .padding(.bottom, 20)
                    
                    // Interactive Footer
                    VStack(spacing: 16) {
                        RecordingButton(isRecording: streamer.isRecording) {
                            feedback()
                            if streamer.isRecording {
                                streamer.stopRecording()
                            } else {
                                streamer.startRecording()
                            }
                        }
                        
                        if let error = streamer.errorMessage {
                            Text(error)
                                .font(.system(size: 12, weight: .medium, design: .monospaced))
                                .foregroundStyle(.red.opacity(0.8))
                                .padding(.top, 8)
                        }
                    }
                    .padding(.bottom, 30)
                }
            }
        }
        .preferredColorScheme(.light)
    }
    
    private func feedback() {
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
    }
}

// MARK: - Components

struct StatusIndicator: View {
    let isHealthy: Bool
    let isConnected: Bool
    
    var body: some View {
        ZStack {
            Circle()
                .fill((isHealthy ? (isConnected ? Color.green : Color.orange) : Color.red).opacity(0.2))
                .frame(width: 18, height: 18)
            
            Circle()
                .fill(isHealthy ? (isConnected ? Color.green : Color.orange) : Color.red)
                .frame(width: 8, height: 8)
        }
    }
}

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }
        self.init(.sRGB, red: Double(r) / 255, green: Double(g) / 255, blue:  Double(b) / 255, opacity: Double(a) / 255)
    }
}

#Preview {
    ContentView()
}
