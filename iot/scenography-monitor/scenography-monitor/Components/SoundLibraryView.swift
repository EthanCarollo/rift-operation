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

// MARK: - Subviews

struct SoundFileRow: View {
    let node: SoundManager.FileNode
    @ObservedObject var soundManager: SoundManager
    @ObservedObject var soundTrigger = SoundTrigger.shared
    let buses: [(id: Int, name: String)]
    
    @State private var isExpanded: Bool = false
    
    // Binding Editing State
    @State private var selectedKey: String = ""
    @State private var isValueSpecific: Bool = false
    @State private var valueType: ValueType = .string
    @State private var stringValue: String = ""
    @State private var boolValue: Bool = true
    @State private var isCustomKey: Bool = false
    @State private var customKey: String = ""

    enum ValueType: String, CaseIterable, Identifiable {
        case string = "Text"
        case boolean = "Bool"
        var id: String { self.rawValue }
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Main Row Content
            HStack(spacing: 8) {
                // Bus Route
                let busId = soundManager.soundRoutes[node.name] ?? 0
                let isAssigned = busId != 0
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
                
                // Binding Badge / Toggle Expansion
                let bondCount = soundTrigger.bindings.filter { $0.soundName == node.name }.count
                Button(action: { 
                    withAnimation(.easeInOut(duration: 0.2)) {
                        isExpanded.toggle() 
                    }
                }) {
                    ZStack {
                        if bondCount > 0 {
                            Circle()
                                .fill(Color.blue.opacity(0.1))
                                .frame(width: 20, height: 20)
                        }
                        Image(systemName: isExpanded ? "chevron.up.circle.fill" : "link")
                            .font(.system(size: isExpanded ? 10 : 9))
                            .foregroundColor(isExpanded ? .secondary : (bondCount > 0 ? .blue : .gray.opacity(0.5)))
                    }
                }
                .buttonStyle(.plain)
                .help(bondCount > 0 ? "\(bondCount) bindings" : "Bind to JSON Trigger")
                
                // Route Picker
                Menu {
                    ForEach(buses, id: \.id) { bus in
                        Button(action: {
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
                    .frame(width: 80)
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
            
            // Inline Binding Editor
            if isExpanded {
                VStack(alignment: .leading, spacing: 8) {
                    Divider()
                    
                    // List Existing Bindings
                    let bindings = soundTrigger.bindings.filter { $0.soundName == node.name }
                    if !bindings.isEmpty {
                        ForEach(bindings) { binding in
                            HStack {
                                Image(systemName: "arrow.turn.down.right")
                                    .font(.system(size: 8))
                                    .foregroundColor(.secondary)
                                Text(binding.jsonKey)
                                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                                
                                Spacer()
                                
                                if let val = binding.targetValue {
                                    Text("== \(val)")
                                        .font(.system(size: 9, design: .monospaced))
                                        .padding(2)
                                        .background(Color.blue.opacity(0.1))
                                        .cornerRadius(3)
                                } else {
                                    Text("Any")
                                        .font(.system(size: 9))
                                        .foregroundColor(.secondary)
                                }
                                
                                Button(action: {
                                    SoundTrigger.shared.removeBinding(id: binding.id)
                                }) {
                                    Image(systemName: "xmark.circle")
                                        .foregroundColor(.red.opacity(0.7))
                                        .font(.system(size: 10))
                                }
                                .buttonStyle(.plain)
                            }
                        }
                        Divider().padding(.vertical, 2)
                    }
                    
                    // Add New Control
                    HStack {
                        // Key Selection
                        if isCustomKey {
                            TextField("Key", text: $customKey)
                                .textFieldStyle(.plain)
                                .font(.system(size: 10, design: .monospaced))
                                .frame(width: 80)
                                .overlay(Rectangle().frame(height: 1).foregroundColor(.secondary.opacity(0.3)), alignment: .bottom)
                        } else {
                            Picker("Key", selection: $selectedKey) {
                                Text("Key...").tag("")
                                ForEach(soundTrigger.knownKeys, id: \.self) { key in
                                    Text(key).tag(key)
                                }
                            }
                            .labelsHidden()
                            .controlSize(.mini)
                            .frame(width: 80)
                        }
                        
                        Toggle("Custom", isOn: $isCustomKey)
                            .toggleStyle(.checkbox)
                            .font(.system(size: 9))
                            .labelsHidden()
                        
                        Spacer()
                        
                        // Value Type & Input
                        if isValueSpecific {
                            Picker("Type", selection: $valueType) {
                                ForEach(ValueType.allCases) { type in
                                    Text(type.rawValue).tag(type)
                                }
                            }
                            .labelsHidden()
                            .controlSize(.mini)
                            .frame(width: 50)
                            
                            if valueType == .string {
                                TextField("Val", text: $stringValue)
                                    .textFieldStyle(.plain)
                                    .font(.system(size: 10))
                                    .frame(width: 50)
                                    .overlay(Rectangle().frame(height: 1).foregroundColor(.secondary.opacity(0.3)), alignment: .bottom)
                            } else {
                                Toggle("True?", isOn: $boolValue)
                                    .labelsHidden()
                                    .controlSize(.mini)
                            }
                        } else {
                            Text("Trigger on Any")
                                .font(.system(size: 9))
                                .foregroundColor(.secondary)
                        }
                        
                        Toggle("Val?", isOn: $isValueSpecific)
                            .toggleStyle(.switch)
                            .labelsHidden()
                            .controlSize(.mini)
                            .scaleEffect(0.7)

                        // Add Button
                        Button(action: {
                            let key = isCustomKey ? customKey : selectedKey
                            guard !key.isEmpty else { return }
                            
                            var finalVal: String? = nil
                            if isValueSpecific {
                                if valueType == .string {
                                    finalVal = stringValue
                                } else {
                                    finalVal = boolValue ? "true" : "false"
                                }
                            }
                            
                            SoundTrigger.shared.addBinding(key: key, sound: node.name, value: finalVal)
                            
                            // Reset
                            if isCustomKey { customKey = "" }
                            stringValue = ""
                        }) {
                            Image(systemName: "plus.circle.fill")
                                .foregroundColor(.green)
                        }
                        .buttonStyle(.plain)
                        .disabled((isCustomKey ? customKey.isEmpty : selectedKey.isEmpty))
                    }
                }
                .padding(8)
                .background(Color(nsColor: .controlBackgroundColor).opacity(0.5))
                .cornerRadius(4)
                .padding(.leading, 20) // Indent
                .padding(.bottom, 4)
            }
        }
    }
}


// MARK: - Subviews


