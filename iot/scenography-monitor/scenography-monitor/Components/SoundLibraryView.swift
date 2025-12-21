//
//  SoundLibraryView.swift
//  scenography-monitor
//
//  Created by eth on 21/12/2025.
//

import SwiftUI

struct SoundLibraryView: View {
    @ObservedObject var soundManager = SoundManager.shared
    
    // Default routing: 0 = Not Assigned
    @State private var soundRoutes: [String: Int] = [:]
    
    let buses = [
        (id: 0, name: "None"),
        (id: 1, name: "Nightmare"),
        (id: 2, name: "Dream"),
        (id: 3, name: "Rift"),
        (id: 4, name: "SAS")
    ]
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("SOUND LIBRARY")
                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                    .foregroundColor(.secondary)
                Spacer()
                Button(action: { soundManager.refreshSounds() }) {
                    Image(systemName: "arrow.clockwise")
                        .font(.system(size: 10))
                }
                .buttonStyle(.plain)
            }
            .padding(8)
            .background(Color(nsColor: .controlBackgroundColor))
            .border(Color(nsColor: .separatorColor), width: 1, edges: [.bottom])
            
            // Usage Hint
            if soundManager.rootNodes.isEmpty {
                VStack(spacing: 8) {
                    Text("No sounds found")
                        .font(.system(size: 10))
                        .foregroundColor(.secondary)
                    Text("Put audio files in:")
                        .font(.system(size: 9))
                        .foregroundColor(.secondary)
                    Text("~/Documents/rift-operation-sounds")
                        .font(.system(size: 9, weight: .bold, design: .monospaced))
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                        .onTapGesture {
                            NSWorkspace.shared.selectFile(nil, inFileViewerRootedAtPath: soundManager.soundDirectoryURL.path)
                        }
                }
                .frame(maxHeight: .infinity)
            } else {
                List {
                    OutlineGroup(soundManager.rootNodes, children: \.children) { node in
                        if node.isDirectory {
                            HStack {
                                Image(systemName: "folder")
                                    .foregroundColor(.secondary)
                                Text(node.name)
                                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                            }
                        } else {
                            SoundFileRow(node: node, soundManager: soundManager, buses: buses, soundRoutes: $soundRoutes)
                        }
                    }
                }
                .listStyle(.plain)
            }
        }
        .background(Color(nsColor: .textBackgroundColor)) // White background
        .border(Color(nsColor: .separatorColor), width: 1, edges: [.trailing])
    }
}

struct SoundFileRow: View {
    let node: SoundManager.FileNode
    @ObservedObject var soundManager: SoundManager
    let buses: [(id: Int, name: String)]
    @Binding var soundRoutes: [String: Int]
    
    var body: some View {
        HStack(spacing: 8) {
            // Bus Route
            let busId = soundRoutes[node.name] ?? 0 // Default to 0 (None)
            let isAssigned = busId != 0
            let isPlaying = isAssigned && soundManager.currentSoundOnBus[busId] == node.name
            
            // Play Button
            Button(action: {
                if isAssigned {
                    if isPlaying {
                        soundManager.stopSound(onBus: busId)
                    } else {
                        soundManager.playSound(node: node, onBus: busId)
                    }
                }
            }) {
                Image(systemName: isPlaying ? "stop.fill" : "play.fill")
                    .font(.system(size: 10))
                    .foregroundColor(isPlaying ? .red : (isAssigned ? .green : .gray))
                    .frame(width: 16, height: 16)
                    .background(Color.black.opacity(0.05))
                    .cornerRadius(4)
            }
            .buttonStyle(.plain)
            .disabled(!isAssigned)
            
            Text(node.name)
                .font(.system(size: 11, design: .monospaced))
                .lineLimit(1)
                .truncationMode(.middle)
            
            Spacer()
            
            // Route Picker (Full Chip)
            Menu {
                ForEach(buses, id: \.id) { bus in
                    Button(action: {
                        // Stop if currently playing on old bus
                        if let oldBus = soundRoutes[node.name], oldBus != 0, soundManager.currentSoundOnBus[oldBus] == node.name {
                            soundManager.stopSound(onBus: oldBus)
                        }
                        soundRoutes[node.name] = bus.id
                    }) {
                        Text(bus.name)
                        if (soundRoutes[node.name] ?? 0) == bus.id {
                            Image(systemName: "checkmark")
                        }
                    }
                }
            } label: {
                let currentBusId = soundRoutes[node.name] ?? 0
                let busName = buses.first(where: { $0.id == currentBusId })?.name ?? "None"
                
                HStack {
                    Text(busName.uppercased())
                        .font(.system(size: 9, weight: .bold, design: .monospaced))
                    Spacer()
                    Image(systemName: "chevron.down")
                        .font(.system(size: 8))
                }
                .foregroundColor(currentBusId == 0 ? .secondary : .primary)
                .padding(.horizontal, 6)
                .padding(.vertical, 3)
                .frame(width: 80) // Wider fixed width
                .background(Color.gray.opacity(0.1))
                .cornerRadius(4)
                .overlay(
                    RoundedRectangle(cornerRadius: 4)
                        .stroke(Color.gray.opacity(0.2), lineWidth: 1)
                )
            }
            .menuStyle(.borderlessButton)
            .frame(width: 80)
        }
        .padding(.vertical, 2)
    }
}
