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
    
    // No more sheet state here, logic moves to rows

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("LIBRARY")
                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                    .foregroundColor(.secondary)
                
                Spacer()
                
                // Filter Picker
                Picker("Filter", selection: $filterId) {
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
                
                // Import
                Button(action: { soundManager.importSounds() }) {
                    Image(systemName: "plus")
                        .font(.system(size: 10, weight: .bold))
                }
                .buttonStyle(.plain)
                .help("Add Sounds")
                .padding(.horizontal, 4)
                
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
                                SoundRow(node: node, soundManager: soundManager, buses: allBuses)
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
                                SoundRow(node: node, soundManager: soundManager, buses: allBuses)
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

// MARK: - Subviews

// SoundFileRow moved to AppUI.swift


// MARK: - Subviews


