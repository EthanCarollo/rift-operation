//
//  ContentView.swift
//  scenography-monitor
//
//  Created by eth on 21/12/2025.
//

import SwiftUI

struct ContentView: View {
    @StateObject private var soundManager = SoundManager.shared
    @State private var isInspectorOpen: Bool = false
    @State private var showOutputList: Bool = true // Default to true for user request
    
    var body: some View {
        VStack(spacing: 0) {
            // Top Toolbar (High tech look)
            HStack(spacing: 0) {
                // Logo Area
                HStack(spacing: 8) {
                    Image("RiftLogo")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(height: 24)
                    
                    Text("RIFT OP // SOUND MONITOR")
                        .font(.system(size: 11, weight: .bold, design: .monospaced))
                        .opacity(0.8)
                }
                .padding(.horizontal, 12)
                
                Spacer()
                
                // Network Config
                Button(action: {
                    withAnimation {
                        isInspectorOpen.toggle()
                    }
                }) {
                    HStack(spacing: 6) {
                        Image(systemName: "network")
                        Text("NET CHECK")
                    }
                    .font(.system(size: 10, weight: .semibold))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(isInspectorOpen ? Color.blue.opacity(0.2) : Color.clear)
                    .foregroundColor(isInspectorOpen ? .blue : .primary)
                    .overlay(
                        RoundedRectangle(cornerRadius: 4)
                            .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                    )
                }
                .buttonStyle(.plain)
                .padding(.trailing, 8)
                
                // Output List Toggle
                Button(action: {
                    withAnimation {
                        showOutputList.toggle()
                    }
                }) {
                    Image(systemName: "sidebar.right")
                        .font(.system(size: 12))
                        .foregroundColor(showOutputList ? .blue : .secondary)
                        .padding(6)
                        .background(Color(nsColor: .controlBackgroundColor))
                        .cornerRadius(4)
                }
                .buttonStyle(.plain)
                .padding(.trailing, 12)
            }
            .frame(height: 48)
            .background(Color(nsColor: .windowBackgroundColor))
            .border(Color(nsColor: .separatorColor), width: 1, edges: [.bottom])

            // Main Content Area (HSplitView)
            HSplitView {
                // Left: Sound Library
                SoundLibraryView()
                    .frame(minWidth: 200, maxWidth: 400)
                
                // Center: Mixer
                ZStack {
                    Color(nsColor: .lightGray).opacity(0.1) // Subtle background check
                        .ignoresSafeArea()
                    
                    ScrollView(.horizontal, showsIndicators: true) {
                        HStack(spacing: 1) {
                            ForEach(soundManager.audioBuses) { bus in
                                AudioBusView(busName: bus.name, busId: bus.id)
                                    .frame(width: 90)
                            }
                            
                            // Add Bus Button
                            VStack {
                                Spacer()
                                Button(action: { soundManager.addBus() }) {
                                    VStack(spacing: 4) {
                                        Image(systemName: "plus")
                                            .font(.system(size: 20))
                                        Text("ADD BUS")
                                            .font(.system(size: 9, weight: .bold))
                                    }
                                    .frame(width: 80, height: 200)
                                    .background(Color(nsColor: .controlBackgroundColor).opacity(0.5))
                                    .cornerRadius(8)
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 8)
                                            .stroke(Color.gray.opacity(0.5), style: StrokeStyle(lineWidth: 1, dash: [4]))
                                    )
                                }
                                .buttonStyle(.plain)
                                Spacer()
                            }
                            .padding(.leading, 8)
                        }
                        .padding(.leading, 1) // Tiny offset
                        .frame(maxHeight: .infinity)
                    }
                }
                .frame(minWidth: 300, maxWidth: .infinity)
                
                // Right: Output List (Fixed width or resizable)
                if showOutputList {
                    OutputListView()
                        .frame(minWidth: 150, maxWidth: 250)
                }
                
                // Inspector (Network) - if active
                if isInspectorOpen {
                    WebSocketInspectorView(isVisible: $isInspectorOpen)
                        .frame(width: 300)
                }
            }
            
            // Bottom Status Bar
            HStack {
                // Status Indicators
                HStack(spacing: 6) {
                    Circle().fill(Color.green).frame(width: 6, height: 6)
                    Text("ENGINE READY")
                }
                .foregroundColor(.secondary)
                
                Text("|").foregroundColor(.gray.opacity(0.5))
                
                Text("44.1kHz")
                    .foregroundColor(.secondary)
                
                Spacer()
                
                // Path Display
                HStack(spacing: 6) {
                    Image(systemName: "folder")
                        .font(.system(size: 10))
                    Text(soundManager.soundDirectoryURL.path)
                        .truncationMode(.middle)
                        .lineLimit(1)
                }
                .foregroundColor(.secondary)
                .padding(.horizontal, 8)
                .frame(maxWidth: 400)
                
                Spacer()
                
                Text("DEV BUILD")
                    .font(.system(size: 9, weight: .bold))
                    .padding(2)
                    .background(Color.red)
                    .foregroundColor(.white)
                    .cornerRadius(2)
            }
            .font(.system(size: 10, design: .monospaced))
            .padding(.horizontal, 12)
            .padding(.vertical, 4)
            .background(Color(nsColor: .windowBackgroundColor))
            .border(Color(nsColor: .separatorColor), width: 1, edges: [.top])
        }
        .frame(minWidth: 1000, minHeight: 600)
        .preferredColorScheme(.light)
    }
}


struct OutputListView: View {
    // Mock devices
    let outputs = ["MacBook Pro Speakers", "BlackHole 16ch", "External Headphones", "HDMI (LG Monitor)"]
    @State private var selectedOutput = "MacBook Pro Speakers"
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("OUTPUT ASSIGNMENT")
                    .font(.system(size: 10, weight: .bold))
                    .foregroundColor(.secondary)
                Spacer()
            }
            .padding(8)
            .background(Color(nsColor: .controlBackgroundColor))
            
            Divider()
            
            List {
                Section(header: Text("AVAILABLE DEVICES")) {
                    ForEach(outputs, id: \.self) { output in
                        HStack {
                            Image(systemName: output == selectedOutput ? "speaker.wave.3.fill" : "speaker")
                                .foregroundColor(output == selectedOutput ? .blue : .gray)
                            Text(output)
                                .font(.system(size: 11))
                            Spacer()
                            if output == selectedOutput {
                                Image(systemName: "checkmark")
                                    .font(.system(size: 10))
                                    .foregroundColor(.blue)
                            }
                        }
                        .padding(.vertical, 2)
                        .contentShape(Rectangle()) // Make full row clickable
                        .onTapGesture {
                            selectedOutput = output
                        }
                    }
                }
            }
            .listStyle(.sidebar)
        }
        .background(Color(nsColor: .windowBackgroundColor))
    }
}

// Extension to allow single-edge borders easily
extension View {
    func border(_ color: Color, width: CGFloat, edges: [Edge]) -> some View {
        overlay(EdgeBorder(width: width, edges: edges).foregroundColor(color))
    }
}

struct EdgeBorder: Shape {
    var width: CGFloat
    var edges: [Edge]

    func path(in rect: CGRect) -> Path {
        var path = Path()
        for edge in edges {
            var x: CGFloat {
                switch edge {
                case .top, .bottom, .leading: return rect.minX
                case .trailing: return rect.maxX - width
                }
            }

            var y: CGFloat {
                switch edge {
                case .top, .leading, .trailing: return rect.minY
                case .bottom: return rect.maxY - width
                }
            }

            var w: CGFloat {
                switch edge {
                case .top, .bottom: return rect.width
                case .leading, .trailing: return width
                }
            }

            var h: CGFloat {
                switch edge {
                case .top, .bottom: return width
                case .leading, .trailing: return rect.height
                }
            }
            path.addPath(Path(CGRect(x: x, y: y, width: w, height: h)))
        }
        return path
    }
}
