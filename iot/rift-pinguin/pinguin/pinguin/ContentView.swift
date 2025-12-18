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
            Color.white.ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Top bar with connection status
                HStack {
                    HStack(spacing: 6) {
                        Circle()
                            .fill(streamer.isServerHealthy ? (streamer.isConnected ? Color.green : Color.orange) : Color.red)
                            .frame(width: 8, height: 8)
                        Text(streamer.isServerHealthy ? (streamer.isConnected ? "Connected" : "Standby") : "Offline")
                            .font(.system(size: 12, weight: .medium, design: .monospaced))
                            .foregroundStyle(streamer.isServerHealthy ? (streamer.isConnected ? .green : .orange) : .red)
                    }
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(Capsule().fill(Color.black.opacity(0.05)))
                    
                    Spacer()
                }
                .padding()
                
                VStack(spacing: 30) {
                    HeaderView()
                    
                    // Latest Answer Display
                    if !streamer.latestAnswer.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("RÉPONSE")
                                .font(.system(size: 10, weight: .bold))
                                .foregroundStyle(.gray)
                                .tracking(2)
                            
                            Text(streamer.latestAnswer)
                                .font(.system(size: 18, weight: .medium, design: .serif))
                                .foregroundStyle(.black)
                                .lineSpacing(4)
                        }
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(
                            RoundedRectangle(cornerRadius: 16)
                                .fill(Color.black.opacity(0.03))
                        )
                        .padding(.horizontal)
                        .transition(.move(edge: .top).combined(with: .opacity))
                    }
                    
                    LogView(text: streamer.transcribedText)
                    
                    RecordingButton(isRecording: streamer.isRecording) {
                        if streamer.isRecording {
                            streamer.stopRecording()
                        } else {
                            streamer.startRecording()
                        }
                    }
                    
                    if let error = streamer.errorMessage {
                        Text(error)
                            .font(.caption)
                            .foregroundStyle(.red)
                            .padding()
                    }
                }
                .padding(.top, 10)
            }
        }
        .animation(.spring(), value: streamer.latestAnswer)
        .preferredColorScheme(.light)
    }
}

#Preview {
    ContentView()
}
