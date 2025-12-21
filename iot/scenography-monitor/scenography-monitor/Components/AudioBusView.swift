//
//  AudioBusView.swift
//  scenography-monitor
//
//  Created by eth on 21/12/2025.
//

import SwiftUI
import AppKit // Required for NSCursor

struct AudioBusView: View {
    let busName: String
    let busId: Int
    @State private var volume: Double = 0.75
    @State private var pan: Double = 0.5
    @State private var isMuted: Bool = false
    @State private var isSolo: Bool = false
    @State private var selectedDevice: String = ""
    
    // Mock devices
    let devices = ["Built-in Output", "Scarlett 2i2", "Virtual Cable 1", "HDMI Audio"]
    
    var body: some View {
        VStack(spacing: 0) {
            // Bus Header
            Text(busName)
                .font(.system(size: 10, weight: .bold, design: .monospaced))
                .foregroundColor(.black)
                .frame(height: 30)
                .frame(maxWidth: .infinity)
                .background(Color(nsColor: .windowBackgroundColor))
                .border(Color(nsColor: .separatorColor), width: 0.5)
            
            // FX/Inserts Placeholder
            VStack(spacing: 1) {
                ForEach(0..<4) { _ in
                    Rectangle()
                        .fill(Color(nsColor: .controlBackgroundColor))
                        .frame(height: 16)
                        .overlay(
                            Rectangle()
                                .stroke(Color(nsColor: .separatorColor).opacity(0.3), lineWidth: 0.5)
                        )
                }
            }
            .padding(1)
            .background(Color(nsColor: .textBackgroundColor))
            
            Divider()
            
            // Controls Area
            VStack(spacing: 8) {
                
                // Pan Knob
                ZStack {
                    Circle()
                        .stroke(Color.gray, lineWidth: 1)
                        .frame(width: 32, height: 32)
                        .background(Circle().fill(Color(nsColor: .windowBackgroundColor)))
                    
                    // Indicator
                    Rectangle()
                        .fill(Color.black)
                        .frame(width: 2, height: 10)
                        .offset(y: -8)
                        .rotationEffect(.degrees((pan * 270) - 135))
                }
                .padding(.top, 8)
                .gesture(
                    DragGesture(minimumDistance: 0)
                        .onChanged { value in
                            NSCursor.hide() // Hide cursor for effect
                            // Allow dragging up/right to increase, down/left to decrease
                            let sensitivity: Double = 0.005
                            let delta = value.translation.width - value.translation.height // Combine axes
                            pan = max(0, min(1, pan + (delta * sensitivity)))
                        }
                        .onEnded { _ in
                            NSCursor.unhide() // Restore cursor
                        }
                )
                
                // Fader & Meter Section
                HStack(alignment: .bottom, spacing: 4) {
                    
                    // Meter L
                    ZStack(alignment: .bottom) {
                        Rectangle()
                            .fill(Color.black.opacity(0.1))
                            .frame(width: 6, height: 160)
                        
                        LinearGradient(
                            gradient: Gradient(colors: [.green, .yellow, .red]),
                            startPoint: .bottom,
                            endPoint: .top
                        )
                        .frame(width: 6, height: 0)
                    }
                    
                    // Fader Track
                    GeometryReader { geo in
                        ZStack(alignment: .bottom) {
                            // Track Background
                            Rectangle()
                                .fill(Color(nsColor: .controlBackgroundColor))
                                .frame(width: 24, height: geo.size.height)
                                .overlay(
                                    Rectangle()
                                        .fill(Color.black.opacity(0.1))
                                        .frame(width: 1)
                                )
                            
                            // Fader Handle
                            Rectangle()
                                .fill(Color(nsColor: .windowBackgroundColor))
                                .frame(width: 24, height: 32)
                                .overlay(
                                    Rectangle()
                                        .fill(Color.black.opacity(0.5))
                                        .frame(height: 1)
                                )
                                .shadow(radius: 1, y: 1)
                                .offset(y: -((volume) * (geo.size.height - 32))) // Position from bottom
                                .gesture(
                                    DragGesture(minimumDistance: 0)
                                        .onChanged { value in
                                            NSCursor.hide()
                                            // Calculate volume based on touch position relative to track height
                                            let trackHeight = geo.size.height
                                            let handleHeight: CGFloat = 32
                                            let usableHeight = trackHeight - handleHeight
                                            
                                            // Invert Y because 0 is at top
                                            let touchYFromBottom = trackHeight - value.location.y - (handleHeight / 2)
                                            
                                            // Normalize
                                            let newVol = touchYFromBottom / usableHeight
                                            volume = max(0, min(1, newVol))
                                        }
                                        .onEnded { _ in
                                            NSCursor.unhide()
                                        }
                                )
                        }
                    }
                    .frame(width: 24, height: 160)
                    
                    // Meter R
                    ZStack(alignment: .bottom) {
                        Rectangle()
                            .fill(Color.black.opacity(0.1))
                            .frame(width: 6, height: 160)
                        
                        LinearGradient(
                            gradient: Gradient(colors: [.green, .yellow, .red]),
                            startPoint: .bottom,
                            endPoint: .top
                        )
                        .frame(width: 6, height: 0)
                    }
                }
                
                // Mute/Solo
                HStack(spacing: 2) {
                    Button(action: { isMuted.toggle() }) {
                        Text("M")
                            .font(.system(size: 8, weight: .bold))
                            .frame(width: 16, height: 16)
                    }
                    .buttonStyle(.plain)
                    .background(isMuted ? Color.red : Color(nsColor: .controlBackgroundColor))
                    .foregroundColor(isMuted ? .white : .secondary)
                    .cornerRadius(2)
                    
                    Button(action: { isSolo.toggle() }) {
                        Text("S")
                            .font(.system(size: 8, weight: .bold))
                            .frame(width: 16, height: 16)
                    }
                    .buttonStyle(.plain)
                    .background(isSolo ? Color.yellow : Color(nsColor: .controlBackgroundColor))
                    .foregroundColor(isSolo ? .black : .secondary)
                    .cornerRadius(2)
                }
            }
            .padding(.bottom, 8)
            .frame(maxWidth: .infinity)
            .background(Color(nsColor: .controlBackgroundColor).opacity(0.5))
            
            Divider()
            
            // Output Picker
            VStack(spacing: 2) {
                Text("OUTPUT")
                    .font(.system(size: 8, weight: .bold))
                    .foregroundColor(.secondary)
                
                Picker("", selection: $selectedDevice) {
                    Text("-- Out --").tag("")
                    ForEach(devices, id: \.self) { device in
                        Text(device).tag(device)
                    }
                }
                .labelsHidden()
                .controlSize(.mini)
                .frame(maxWidth: 80)
            }
            .frame(height: 50)
            .frame(maxWidth: .infinity)
            .background(Color(nsColor: .windowBackgroundColor))
        }
        .frame(width: 90)
        .background(Color(nsColor: .windowBackgroundColor))
        .border(Color(nsColor: .separatorColor), width: 0.5)
    }
}
