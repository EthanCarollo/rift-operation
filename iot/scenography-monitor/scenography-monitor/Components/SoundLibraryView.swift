//
//  SoundLibraryView.swift
//  scenography-monitor
//
//  Created by eth on 21/12/2025.
//

import SwiftUI

struct SoundLibraryView: View {
    @ObservedObject var soundManager = SoundManager.shared
    
    // Default routing is 0 (None), managed by soundManager.soundRoutes
    // Filter State: -1 = All, 0 = Unassigned, 1+ = Bus ID
    @State private var filterId: Int = -1
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("LIBRARY")
                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                    .foregroundColor(.secondary)
                
                Spacer()
                
                // Filter Picker
                Picker("", selection: $filterId) {
                    Text("ALL").tag(-1)
                    Divider()
                    Text("Unassigned").tag(0)
                    ForEach(soundManager.audioBuses, id: \.id) { bus in
                        Text(bus.name.uppercased()).tag(bus.id)
                    }
                }
                .labelsHidden()
                .controlSize(.mini)
                .frame(width: 90)
                
                // Folder Selection
                Button(action: { soundManager.selectSoundDirectory() }) {
                    Image(systemName: "folder")
                        .font(.system(size: 10))
                }
                .buttonStyle(.plain)
                .padding(.horizontal, 4)
                
                // Refresh
                Button(action: { soundManager.refreshSounds() }) {
                    Image(systemName: "arrow.clockwise")
                        .font(.system(size: 10))
                }
                .buttonStyle(.plain)
            }
            .padding(8)
            .background(Color(nsColor: .controlBackgroundColor))
            .border(Color(nsColor: .separatorColor), width: 1, edges: [.bottom])
            
            // Dynamic Bus List for Rows
            let allBuses = [(id: 0, name: "None")] + soundManager.audioBuses.map { (id: $0.id, name: $0.name) }
            
            // Usage Hint
            if soundManager.rootNodes.isEmpty {
                VStack(spacing: 8) {
                    Text("No sounds found in:")
                        .font(.system(size: 10))
                        .foregroundColor(.secondary)
                    
                    // Debug Path
                    Text(soundManager.soundDirectoryURL.path)
                        .font(.system(size: 8, design: .monospaced))
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                        
                    Button("Select Folder") {
                        soundManager.selectSoundDirectory()
                    }
                }
                .frame(maxHeight: .infinity)
            } else {
                List {
                    if filterId == -1 {
                        // Hierarchical View (Default)
                        OutlineGroup(soundManager.rootNodes, children: \.children) { node in
                            if node.isDirectory {
                                HStack {
                                    Image(systemName: "folder")
                                        .foregroundColor(.secondary)
                                    Text(node.name)
                                        .font(.system(size: 11, weight: .bold, design: .monospaced))
                                }
                            } else {
                                SoundFileRow(node: node, soundManager: soundManager, buses: allBuses)
                            }
                        }
                    } else {
                        // Filtered Flat View
                        let filteredNodes = soundManager.getAllFiles().filter { node in
                            if node.isDirectory { return false }
                            let assignedBus = soundManager.soundRoutes[node.name] ?? 0
                            return assignedBus == filterId
                        }
                        
                        if filteredNodes.isEmpty {
                            Text("No sounds found for filter.")
                                .font(.system(size: 10))
                                .foregroundColor(.secondary)
                                .padding()
                        } else {
                            ForEach(filteredNodes) { node in
                                SoundFileRow(node: node, soundManager: soundManager, buses: allBuses)
                            }
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
    
    var body: some View {
        HStack(spacing: 8) {
            // Bus Route
            let busId = soundManager.soundRoutes[node.name] ?? 0
            let isAssigned = busId != 0
            // isPlaying logic: check if this BUS is playing AND if the sound on it is THIS one.
            // But wait, AudioBusView only knows 'busId'.
            // SoundManager knows 'activeBusIds'.
            // SoundManager logic confirms that if a bus is active, the sound routed to it IS playing?
            // Actually, playSound() sets activeBusId.
            // And playSound() updates route.
            // So if activeBusIds contains busId, AND route matches, it's playing.
            let isPlaying = isAssigned && soundManager.activeBusIds.contains(busId)
            
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
                        if let oldBus = soundManager.soundRoutes[node.name], oldBus != 0, soundManager.activeBusIds.contains(oldBus) {
                            soundManager.stopSound(onBus: oldBus)
                        }
                        soundManager.soundRoutes[node.name] = bus.id
                    }) {
                        Text(bus.name)
                        if (soundManager.soundRoutes[node.name] ?? 0) == bus.id {
                            Image(systemName: "checkmark")
                        }
                    }
                }
            } label: {
                let currentBusId = soundManager.soundRoutes[node.name] ?? 0
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
