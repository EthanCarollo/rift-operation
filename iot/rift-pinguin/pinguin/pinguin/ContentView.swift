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
            
            VStack(spacing: 40) {
                
                HeaderView()
                
                // Connection status indicator
                HStack(spacing: 8) {
                    Circle()
                        .fill(streamer.isConnected ? Color.green : Color.gray)
                        .frame(width: 10, height: 10)
                    Text(streamer.isConnected ? "Connected" : "Disconnected")
                        .font(.caption)
                        .foregroundStyle(streamer.isConnected ? .green : .gray)
                }
                .padding(.horizontal)
                .padding(.vertical, 6)
                .background(
                    Capsule()
                        .fill(Color.black.opacity(0.05))
                )
                
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
        }
        .preferredColorScheme(.light)
    }
}

#Preview {
    ContentView()
}
