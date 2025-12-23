
import SwiftUI

struct SoundRow: View {
    let node: SoundManager.FileNode
    @ObservedObject var soundManager: SoundManager
    @ObservedObject var soundTrigger = SoundTrigger.shared
    let buses: [(id: Int, name: String)]
    
    // Local State
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
                let isPlaying = isAssigned && soundManager.activeBusIds.contains(busId) && soundManager.activeNodeNames[busId] == node.name
                let isLoading = isAssigned && soundManager.loadingBusIds.contains(busId)
                
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
                    if isLoading {
                         ProgressView()
                             .scaleEffect(0.5)
                             .frame(width: 16, height: 16)
                    } else {
                        Image(systemName: isPlaying ? "stop.fill" : "play.fill")
                            .font(.system(size: 10))
                            .foregroundColor(isPlaying ? .red : (isAssigned ? .green : .gray))
                            .frame(width: 16, height: 16)
                            .background(Color.black.opacity(0.05))
                            .cornerRadius(4)
                    }
                }
                .buttonStyle(.plain)
                .disabled(!isAssigned || isLoading)
                
                Text(node.name)
                    .font(.system(size: 11, design: .monospaced))
                    .lineLimit(1)
                    .truncationMode(.middle)
                    .onDrag {
                        return NSItemProvider(object: node.name as NSString)
                    }
                
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
                
                // Route Picker (Simplified - "Just with a down arrow")
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
                    let busName = buses.first(where: { $0.id == currentBusId })?.name ?? "NONE"
                    
                    HStack(spacing: 4) {
                        Text(busName.uppercased())
                            .font(.system(size: 9, weight: .bold, design: .monospaced))
                            .foregroundColor(currentBusId == 0 ? .secondary : .primary)
                        
                        Image(systemName: "chevron.down")
                            .font(.system(size: 8, weight: .bold))
                            .foregroundColor(.secondary)
                    }
                    .padding(.vertical, 4)
                    .padding(.horizontal, 4)
                    // Removed Background/Border for minimal look
                    .contentShape(Rectangle()) // Ensure click area
                }
                .menuStyle(.borderlessButton)
                .frame(width: 80, alignment: .trailing) // Align text to right or center? Trailing keeps it neat.
            }
            .padding(.vertical, 2)
            
            // Inline Binding Editor
            if isExpanded {
                bindingEditor
            }
        }
    }
    
    var bindingEditor: some View {
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
