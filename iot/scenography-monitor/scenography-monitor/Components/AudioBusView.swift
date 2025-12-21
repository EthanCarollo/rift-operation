//
//  AudioBusView.swift
//  scenography-monitor
//
//  Created by eth on 21/12/2025.
//

import SwiftUI
import AVFoundation

struct AudioBusView: View {
    let busName: String
    let busId: Int
    
    @ObservedObject var soundManager = SoundManager.shared
    
    // Retrieve the bus model from manager
    private var bus: SoundManager.AudioBus? {
        soundManager.audioBuses.first(where: { $0.id == busId })
    }
    
    // Drag States
    @State private var isDraggingKnob: Bool = false
    @State private var isDraggingFader: Bool = false
    @State private var initialValue: Double = 0.0
    @State private var initialMouseLocation: CGPoint? = nil
    
    @State private var selectedDevice: String = "" 
    
    var body: some View {
        // Safe unwrap of bus settings
        let currentVolume = Double(bus?.volume ?? 0.75)
        let currentPan = Double(bus?.pan ?? 0.5)
        let isMuted = bus?.isMuted ?? false
        let isSolo = bus?.isSolo ?? false
        
        return VStack(spacing: 0) {
            // Bus Header
            Text("BUS \(busId)")
                .font(.system(size: 8, weight: .heavy))
                .foregroundColor(.secondary)
                .frame(maxWidth: .infinity)
                .padding(.top, 4)
            
            TextField("Name", text: Binding(
                get: { bus?.name ?? "BUS \(busId)" },
                set: { soundManager.setBusName($0, onBus: busId) }
            ))
            .font(.system(size: 10, weight: .bold, design: .monospaced))
            .multilineTextAlignment(.center)
            .textFieldStyle(.plain)
            .foregroundColor(.black)
            .frame(height: 16)
            .frame(maxWidth: .infinity)
            .background(Color(nsColor: .windowBackgroundColor))
            .border(Color(nsColor: .separatorColor), width: 0.5)
            
            // FX/Inserts / Info Area
            VStack(spacing: 1) {
                Spacer().frame(height: 4)
                
                // Visual Placeholder lines (FX slots)
                ForEach(0..<2) { _ in
                    Rectangle()
                        .fill(Color(nsColor: .controlBackgroundColor))
                        .frame(height: 12)
                        .overlay(
                            Rectangle()
                                .stroke(Color(nsColor: .separatorColor).opacity(0.3), lineWidth: 0.5)
                        )
                }
            }
            .padding(2)
            .background(Color(nsColor: .textBackgroundColor))
            
            Divider()
            
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
                        .rotationEffect(.degrees((currentPan * 270) - 135))
                }
                .padding(.top, 8)
                .help("Pan Control (Left/Right)")
                .gesture(
                    DragGesture(minimumDistance: 0)
                        .onChanged { value in
                            if !isDraggingKnob {
                                isDraggingKnob = true
                                initialValue = currentPan
                                if let event = CGEvent(source: nil) {
                                    initialMouseLocation = event.location
                                }
                                NSCursor.hide()
                            }
                            let sensitivity: Double = 0.002
                            let delta = value.translation.width - value.translation.height // Combine axes
                            let newPan = max(0, min(1, initialValue + (delta * sensitivity)))
                            soundManager.setPan(Float(newPan), onBus: busId)
                        }
                        .onEnded { _ in
                            isDraggingKnob = false
                            if let loc = initialMouseLocation {
                                CGWarpMouseCursorPosition(loc)
                            }
                            NSCursor.unhide()
                        }
                )
                
                // Fader & Meter Section
                HStack(alignment: .bottom, spacing: 4) {
                    
                    // Live Meter (Left)
                    GeometryReader { geo in
                        ZStack(alignment: .bottom) {
                            Rectangle()
                                .fill(Color.black.opacity(0.1))
                                .frame(width: 6, height: geo.size.height)
                            
                            // Dynamic Level Bar
                            let level = CGFloat(soundManager.busLevels[busId] ?? 0.0)
                            LinearGradient(
                                gradient: Gradient(colors: [.green, .yellow, .red]),
                                startPoint: .bottom,
                                endPoint: .top
                            )
                            .frame(width: 6, height: min(level, 1.0) * geo.size.height)
                            .animation(.linear(duration: 0.05), value: level)
                        }
                    }
                    .frame(width: 6)
                    
                    // Fader Track (Right)
                    GeometryReader { geo in
                        ZStack(alignment: .bottom) {
                            // Track Background
                            Rectangle()
                                .fill(Color(nsColor: .controlBackgroundColor))
                                .frame(width: 24, height: geo.size.height)
                                .overlay(
                                    Rectangle()
                                        .stroke(Color.black.opacity(0.1), lineWidth: 1)
                                )
                            
                            // Fader Cap
                            Rectangle()
                                .fill(Color(nsColor: .windowBackgroundColor))
                                .frame(width: 24, height: 32)
                                .overlay(
                                    Rectangle()
                                        .fill(Color.black.opacity(0.5))
                                        .frame(height: 1)
                                )
                                .shadow(radius: 1, y: 1)
                                .offset(y: -((currentVolume) * (geo.size.height - 32))) // Position
                                .gesture(
                                    DragGesture(minimumDistance: 0)
                                        .onChanged { value in
                                            if !isDraggingFader {
                                                isDraggingFader = true
                                                initialValue = currentVolume
                                                if let event = CGEvent(source: nil) {
                                                    initialMouseLocation = event.location
                                                }
                                                NSCursor.hide()
                                            }
                                            
                                            let sensitivity: Double = 0.003
                                            let delta = -value.translation.height
                                            let newVol = max(0, min(1, initialValue + (delta * sensitivity)))
                                            
                                            soundManager.setVolume(Float(newVol), onBus: busId)
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
                    .frame(width: 24)
                }
                .frame(maxHeight: .infinity)
                .help("Volume Fader")
                
                // Mute/Solo
                HStack(spacing: 4) { // Increased spacing
                    Button(action: { soundManager.toggleMute(onBus: busId) }) {
                        Text("M")
                            .font(.system(size: 12, weight: .bold)) // Larger Font
                            .frame(width: 28, height: 28) // Larger Button
                    }
                    .buttonStyle(.plain)
                    .background(isMuted ? Color.orange : Color.gray.opacity(0.2))
                    .foregroundColor(isMuted ? .white : .primary)
                    .cornerRadius(4) // More rounded
                    .help("Mute Channel")
                    
                    Button(action: { soundManager.toggleSolo(onBus: busId) }) {
                        Text("S")
                            .font(.system(size: 12, weight: .bold)) // Larger Font
                            .frame(width: 28, height: 28) // Larger Button
                    }
                    .buttonStyle(.plain)
                    .background(isSolo ? Color.green : Color.gray.opacity(0.2))
                    .foregroundColor(isSolo ? .white : .primary)
                    .cornerRadius(4)
                    .help("Solo Channel (Mutes others)")
                }
            }
            .padding(.bottom, 8)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Color(nsColor: .controlBackgroundColor).opacity(0.5))
            
            Divider()
            
            // Output Picker
            VStack(spacing: 2) {
                Text("OUTPUT")
                    .font(.system(size: 8, weight: .bold))
                    .foregroundColor(.secondary)
                
                Picker("", selection: Binding(
                    get: { bus?.outputDeviceName ?? "System/Default" },
                    set: { soundManager.setOutput($0, onBus: busId) }
                )) {
                    Text("System Default").tag("System/Default")
                    Text("-- Out --").tag("")
                    ForEach(soundManager.availableOutputs, id: \.self) { device in
                        Text(device).tag(device)
                    }
                }
                .labelsHidden()
                .controlSize(.mini)
                .frame(maxWidth: 80)
            }
            .frame(height: 50)
            .frame(maxWidth: .infinity)
            .background(Color(hex: bus?.colorHex ?? "#F0F0F0"))
        }
        .frame(width: 90)
        .frame(maxHeight: .infinity)
        .background(Color(hex: bus?.colorHex ?? "#F0F0F0"))
        .border(Color(nsColor: .separatorColor), width: 0.5)
        .contextMenu {
            Text("Bus Color")
            Button("Reset") { soundManager.setBusColor("#F0F0F0", onBus: busId) }
            Divider()
            ForEach(PastelColor.allCases, id: \.self) { color in
                Button(action: {
                    soundManager.setBusColor(color.hex, onBus: busId)
                }) {
                    HStack {
                        Image(systemName: "circle.fill")
                            .foregroundColor(Color(hex: color.hex))
                        Text(color.name)
                    }
                }
            }
        }
    }
}

enum PastelColor: CaseIterable {
    case orange, blue, green, pink, purple, yellow, gray, white
    
    var name: String {
        switch self {
        case .orange: return "Pastel Orange"
        case .blue: return "Pastel Blue"
        case .green: return "Pastel Green"
        case .pink: return "Pastel Pink"
        case .purple: return "Pastel Purple"
        case .yellow: return "Pastel Yellow"
        case .gray: return "Light Gray"
        case .white: return "White"
        }
    }
    
    var hex: String {
        switch self {
        case .orange: return "#FFD1A4"
        case .blue: return "#AEC6CF"
        case .green: return "#B0E57C"
        case .pink: return "#F4C2C2"
        case .purple: return "#C3B1E1"
        case .yellow: return "#FDFD96"
        case .gray: return "#F0F0F0"
        case .white: return "#FFFFFF"
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
        
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}
