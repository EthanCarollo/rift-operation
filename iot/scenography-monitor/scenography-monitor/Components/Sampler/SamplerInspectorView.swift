
import SwiftUI

struct SamplerInspectorView: View {
    @ObservedObject var soundManager = SoundManager.shared
    @ObservedObject var soundTrigger = SoundTrigger.shared
    
    // Binding Editing State (Local to inspector)
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
    
    @State private var isStopTrigger: Bool = false  // For stop trigger bindings
    
    var body: some View {
        HStack(spacing: 0) {
            if let selectedId = soundManager.selectedInstanceId,
               let instance = findInstance(by: selectedId) {
                
                VStack(alignment: .leading, spacing: 0) {
                    // Inspector Header
                    HStack {
                        Image(systemName: "slider.horizontal.3")
                        Text("Inspector: \(instance.filename)")
                            .font(.headline)
                        Spacer()
                        Button(action: {
                            soundManager.selectedInstanceId = nil
                        }) {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundColor(.gray)
                        }
                        .buttonStyle(.plain)
                    }
                    .padding()
                    .background(Color(nsColor: .controlBackgroundColor))
                    
                    Divider()
                    
                    HStack(alignment: .top) {
                        // Left Column: Sound Options + Bindings
                        VStack(alignment: .leading, spacing: 12) {
                            // Sound Options Section
                            VStack(alignment: .leading, spacing: 6) {
                                Text("Sound Options").font(.caption).bold().foregroundColor(.secondary)
                                
                                Toggle("Don't replay if playing", isOn: Binding(
                                    get: { instance.preventReplayWhilePlaying },
                                    set: { soundManager.updateInstance(instance.id, preventReplayWhilePlaying: $0) }
                                ))
                                .font(.caption)
                                .accessibilityIdentifier("preventReplayToggle")
                                
                                Toggle("Loop sound", isOn: Binding(
                                    get: { instance.loopEnabled },
                                    set: { soundManager.updateInstance(instance.id, loopEnabled: $0) }
                                ))
                                .font(.caption)
                                .accessibilityIdentifier("loopEnabledToggle")
                            }
                            .padding(8)
                            .background(Color.black.opacity(0.05))
                            .cornerRadius(6)
                            
                            // Active Bindings
                            Text("Active Bindings").font(.caption).bold().foregroundColor(.secondary)
                            
                            let bindings = soundTrigger.bindings.filter { $0.instanceId == instance.id }
                            
                            ScrollView {
                                if bindings.isEmpty {
                                    Text("No bindings configured")
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                        .padding(.top, 8)
                                } else {
                                    VStack(alignment: .leading, spacing: 4) {
                                        ForEach(bindings) { binding in
                                            HStack {
                                                Image(systemName: binding.isStopTrigger ? "stop.circle" : "play.circle")
                                                    .font(.system(size: 10))
                                                    .foregroundColor(binding.isStopTrigger ? .red : .green)
                                                Text(binding.jsonKey)
                                                    .font(.system(size: 11, design: .monospaced))
                                                Spacer()
                                                if binding.isStopTrigger {
                                                    Text("STOP")
                                                        .font(.caption2)
                                                        .padding(2)
                                                        .background(Color.red.opacity(0.2))
                                                        .foregroundColor(.red)
                                                        .cornerRadius(4)
                                                }
                                                if let val = binding.targetValue {
                                                    Text("== \(val)")
                                                        .font(.caption2)
                                                        .padding(2)
                                                        .background(Color.blue.opacity(0.1))
                                                        .cornerRadius(4)
                                                }
                                                Button {
                                                    soundTrigger.removeBinding(id: binding.id)
                                                } label: {
                                                    Image(systemName: "trash")
                                                        .foregroundColor(.red)
                                                }
                                                .buttonStyle(.plain)
                                            }
                                            .padding(6)
                                            .background(Color.black.opacity(0.1))
                                            .cornerRadius(4)
                                        }
                                    }
                                }
                            }
                        }
                        .frame(width: 280)
                        
                        Divider()
                        
                        // Right: Add Binding Form
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Add Trigger").font(.caption).bold().foregroundColor(.secondary)
                            
                            // Key Selection
                            VStack(alignment: .leading, spacing: 2) {
                                Text("Event Key").font(.caption2)
                                HStack {
                                    if isCustomKey {
                                        TextField("e.g. 'motion'", text: $customKey)
                                            .textFieldStyle(.roundedBorder)
                                    } else {
                                        Picker("Key", selection: $selectedKey) {
                                            Text("Select Key").tag("")
                                            ForEach(soundTrigger.knownKeys, id: \.self) { key in
                                                Text(key).tag(key)
                                            }
                                        }
                                        .labelsHidden()
                                    }
                                    Toggle("Custom", isOn: $isCustomKey).labelsHidden()
                                }
                            }
                            
                            // Value Selection
                            VStack(alignment: .leading, spacing: 2) {
                                Toggle("Value Specific?", isOn: $isValueSpecific)
                                    .font(.caption2)
                                
                                if isValueSpecific {
                                    HStack {
                                        Picker("", selection: $valueType) {
                                            ForEach(ValueType.allCases) { type in
                                                Text(type.rawValue).tag(type)
                                            }
                                        }
                                        .labelsHidden()
                                        .frame(width: 70)
                                        
                                        if valueType == .string {
                                            TextField("Value", text: $stringValue)
                                                .textFieldStyle(.roundedBorder)
                                        } else {
                                            Toggle("True", isOn: $boolValue).labelsHidden()
                                        }
                                    }
                                }
                            }
                            
                            // Stop Trigger Option
                            Toggle("Stop Trigger (stops loop)", isOn: $isStopTrigger)
                                .font(.caption)
                                .accessibilityIdentifier("stopTriggerToggle")
                            
                            Spacer()
                            
                            Button(isStopTrigger ? "Add Stop Binding" : "Add Binding") {
                                addBinding(for: instance)
                            }
                            .disabled((isCustomKey ? customKey.isEmpty : selectedKey.isEmpty))
                        }
                        .padding(.leading)
                    }
                    .padding()
                }
                .background(Color(nsColor: .windowBackgroundColor))
                
            } else {
                // No Selection State
                VStack {
                    Text("Select a sound slot to edit bindings")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color(nsColor: .windowBackgroundColor))
            }
        }
        .frame(minHeight: 200, maxHeight: 400) // Flexible height
        .background(Color(nsColor: .windowBackgroundColor))
        .cornerRadius(12)
        .shadow(radius: 10)
        .padding(.horizontal)
        .padding(.bottom)
    }
    
    private func findInstance(by id: UUID) -> SoundManager.SoundInstance? {
        for (_, instances) in soundManager.busSamples {
            if let instance = instances.first(where: { $0.id == id }) {
                return instance
            }
        }
        return nil
    }
    
    private func addBinding(for instance: SoundManager.SoundInstance) {
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
        
        soundTrigger.addBinding(key: key, sound: instance.filename, instanceId: instance.id, value: finalVal, isStopTrigger: isStopTrigger)
        
        // Reset
        if isCustomKey { customKey = "" }
        stringValue = ""
        isStopTrigger = false
    }
}
