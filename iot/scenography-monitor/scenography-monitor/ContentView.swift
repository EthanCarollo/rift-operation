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
    
    // Selection State
    @State private var selectedBusIds: Set<Int> = []
    @State private var lastSelectedBusId: Int?
    
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
                                AudioBusView(
                                    busName: bus.name, 
                                    busId: bus.id,
                                    isSelected: selectedBusIds.contains(bus.id),
                                    selectedBusIds: selectedBusIds,
                                    onSelection: { handleBusSelection(bus.id) }
                                )
                                .frame(width: 90)
                            }
                        }
                        .padding(.leading, 1) // Tiny offset
                        .frame(maxHeight: .infinity)
                    }
                }
                .frame(minWidth: 300, maxWidth: .infinity)
                
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
        .overlay(
            Group {
                if showOutputList {
                    OutputListView(isVisible: $showOutputList)
                        .frame(width: 250, height: 300)
                        .background(Color(nsColor: .windowBackgroundColor))
                        .cornerRadius(8)
                        .shadow(radius: 5)
                        .padding(.trailing, 20)
                        .padding(.top, 50)
                        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topTrailing)
                }
            }
        )
    }

    private func handleBusSelection(_ busId: Int) {
        let flags = NSEvent.modifierFlags
        
        if flags.contains(.command) {
            // Toggle
            if selectedBusIds.contains(busId) {
                selectedBusIds.remove(busId)
            } else {
                selectedBusIds.insert(busId)
                lastSelectedBusId = busId
            }
        } else if flags.contains(.shift) {
            // Range
            if let last = lastSelectedBusId {
                let start = min(last, busId)
                let end = max(last, busId)
                let range = start...end
                for id in range {
                    selectedBusIds.insert(id)
                }
            } else {
                selectedBusIds = [busId]
                lastSelectedBusId = busId
            }
        } else {
            // Single select
            selectedBusIds = [busId]
            lastSelectedBusId = busId
        }
    }
}


struct OutputListView: View {
    @Binding var isVisible: Bool
    @ObservedObject var soundManager = SoundManager.shared
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("SYSTEM AUDIO DEVICES")
                    .font(.system(size: 10, weight: .bold))
                    .foregroundColor(.secondary)
                Spacer()
                Button(action: { soundManager.refreshAudioDevices() }) {
                    Image(systemName: "arrow.triangle.2.circlepath")
                        .font(.system(size: 10))
                        .foregroundColor(.secondary)
                }
                .buttonStyle(.plain)
                .padding(.trailing, 4)
                
                Button(action: { withAnimation { isVisible = false } }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.gray)
                }
                .buttonStyle(.plain)
            }
            .padding(10)
            .background(Color(nsColor: .controlBackgroundColor))
            
            Divider()
            
            List {
                ForEach(soundManager.availableOutputs, id: \.self) { output in
                    HStack {
                        Image(systemName: "speaker.wave.2")
                            .foregroundColor(.gray)
                        Text(output)
                            .font(.system(size: 11))
                        Spacer()
                    }
                    .padding(.vertical, 2)
                }
            }
            .listStyle(.plain)
        }
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color(nsColor: .separatorColor), lineWidth: 1)
        )
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
