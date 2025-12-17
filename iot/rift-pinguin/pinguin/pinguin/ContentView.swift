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
            Color.black.ignoresSafeArea()
            
            VStack(spacing: 40) {
                
                HeaderView()
                
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
        .preferredColorScheme(.dark)
    }
}

#Preview {
    ContentView()
}
