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
                // Filter Picker Removed (Incompatible with Instance Model)

                
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
                            SoundRow(node: node)
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


