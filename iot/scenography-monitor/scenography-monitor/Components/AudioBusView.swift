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
    let busId: Int
    @State private var volume: Double = 0.75
    @State private var pan: Double = 0.5
    @State private var isMuted: Bool = false
    @State private var isSolo: Bool = false
    @State private var selectedDevice: String = ""
    @State private var selectedSound: String = "" // For file selection
    
    @ObservedObject var soundManager = SoundManager.shared
    
    // Drag States
    @State private var isDraggingKnob: Bool = false
    @State private var isDraggingFader: Bool = false
    @State private var initialValue: Double = 0.0
    @State private var initialMouseLocation: CGPoint? = nil // To store cursor WARP location
    
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
            
            // Sound Player Controls
            VStack(spacing: 4) {
                // Sound Selector
                Menu {
                    Text("Select Sound").foregroundColor(.secondary)
                    Divider()
                    ForEach(soundManager.availableSounds, id: \.self) { sound in
                        Button(action: { selectedSound = sound }) {
                            Text(sound)
                            if selectedSound == sound { Image(systemName: "checkmark") }
                        }
                    }
                } label: {
                    Text(selectedSound.isEmpty ? "LOAD" : selectedSound)
                        .font(.system(size: 8, design: .monospaced))
                        .lineLimit(1)
                        .truncationMode(.middle)
                        .frame(maxWidth: .infinity)
                }
                .menuStyle(.borderlessButton)
                .frame(height: 16)
                .padding(.horizontal, 2)
                
                // Play Button
                Button(action: {
                    if soundManager.isPlaying(onBus: busId) {
                        soundManager.stopSound(onBus: busId)
                    } else {
                        if !selectedSound.isEmpty {
                            soundManager.playSound(named: selectedSound, onBus: busId, volume: Float(volume), pan: Float(pan))
                        }
                    }
                    // Trigger UI update logic if needed, usually observed object handles it but isPlaying might change internally
                    // Forcing a redraw might be needed if isPlaying is not @Published per bus in a way we observe easily here directly without polling or better structure.
                    // For now, simple toggle logic.
                    // Actually, since we don't observe the audioPlayer dictionary deeply, the button state might not auto-update.
                    // We can use a trick or just rely on the user action for now.
                    // A better way is to check the state.
                    objectWillChange.send() // Force update
                    
                }) {
                    Image(systemName: soundManager.isPlaying(onBus: busId) ? "stop.fill" : "play.fill")
                        .font(.system(size: 10))
                        .frame(maxWidth: .infinity, maxHeight: 18)
                        .background(soundManager.isPlaying(onBus: busId) ? Color.green : Color(nsColor: .controlColor))
                        .foregroundColor(soundManager.isPlaying(onBus: busId) ? .white : .primary)
                        .cornerRadius(2)
                }
                .buttonStyle(.plain)
                .disabled(selectedSound.isEmpty)
            }
            .padding(4)
            .background(Color(nsColor: .windowBackgroundColor))
            
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
                            if !isDraggingKnob {
                                isDraggingKnob = true
                                initialValue = pan
                                // Capture current mouse position for restore
                                if let event = CGEvent(source: nil) {
                                    initialMouseLocation = event.location
                                }
                                NSCursor.hide()
                            }
                            // Allow dragging up/right to increase, down/left to decrease
                            let sensitivity: Double = 0.002
                            let delta = value.translation.width - value.translation.height // Combine axes
                            pan = max(0, min(1, initialValue + (delta * sensitivity)))
                        }
                        .onEnded { _ in
                            isDraggingKnob = false
                            // Restore cursor position
                            if let loc = initialMouseLocation {
                                CGWarpMouseCursorPosition(loc)
                            }
                            NSCursor.unhide()
                        }
                )
                
                // Fader & Meter Section
                HStack(alignment: .bottom, spacing: 4) {
                    
                    // Meter L
                    GeometryReader { geo in
                        ZStack(alignment: .bottom) {
                            Rectangle()
                                .fill(Color.black.opacity(0.1))
                                .frame(width: 6, height: geo.size.height)
                            
                            LinearGradient(
                                gradient: Gradient(colors: [.green, .yellow, .red]),
                                startPoint: .bottom,
                                endPoint: .top
                            )
                            .frame(width: 6, height: 0) // Dynamic metering would use geo.size.height * level
                        }
                    }
                    .frame(width: 6)
                    
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
                                            if !isDraggingFader {
                                                isDraggingFader = true
                                                initialValue = volume
                                                if let event = CGEvent(source: nil) {
                                                    initialMouseLocation = event.location
                                                }
                                                NSCursor.hide()
                                            }
                                            
                                            // Relative Drag Logic
                                            let sensitivity: Double = 0.003
                                            // Invert deltaY because dragging UP should increase volume
                                            let delta = -value.translation.height
                                            
                                            volume = max(0, min(1, initialValue + (delta * sensitivity)))
                                        }
                                        .onEnded { _ in
                                            isDraggingFader = false
                                            if let loc = initialMouseLocation {
                                                CGWarpMouseCursorPosition(loc)
                                            }
                                            NSCursor.unhide()
                                        }
                                )
                        }
                    }
                    .frame(width: 24) // Allow flexible height
                    
                    // Meter R
                    GeometryReader { geo in
                        ZStack(alignment: .bottom) {
                            Rectangle()
                                .fill(Color.black.opacity(0.1))
                                .frame(width: 6, height: geo.size.height)
                            
                            LinearGradient(
                                gradient: Gradient(colors: [.green, .yellow, .red]),
                                startPoint: .bottom,
                                endPoint: .top
                            )
                            .frame(width: 6, height: 0)
                        }
                    }
                    .frame(width: 6)
                }
                .frame(maxHeight: .infinity) // Fill available space
                
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
            .frame(maxWidth: .infinity, maxHeight: .infinity) // Make Controls Area fill space
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
        .frame(maxHeight: .infinity) // AudioBusView fills vertical space
        .background(Color(nsColor: .windowBackgroundColor))
        .border(Color(nsColor: .separatorColor), width: 0.5)
    }
}
