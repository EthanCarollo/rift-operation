
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
                        // Left: Existing Bindings List
                        VStack(alignment: .leading) {
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
                                                Image(systemName: "link")
                                                    .font(.system(size: 8))
                                                Text(binding.jsonKey)
                                                    .font(.system(size: 11, design: .monospaced))
                                                Spacer()
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
                        .frame(width: 250)
                        
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
                            
                            Spacer()
                            
                            Button("Add Binding") {
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
        .frame(height: 200) // Fixed height for Inspector Panel
        .border(Color.gray.opacity(0.2), width: 1, edges: [.top])
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
        
        soundTrigger.addBinding(key: key, sound: instance.filename, instanceId: instance.id, value: finalVal)
        
        // Reset
        if isCustomKey { customKey = "" }
        stringValue = ""
    }
}
