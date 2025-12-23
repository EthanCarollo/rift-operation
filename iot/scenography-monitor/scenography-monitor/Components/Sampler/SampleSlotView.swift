
import SwiftUI

struct SampleSlotView: View {
    let instance: SoundManager.SoundInstance
    let busId: Int
    @ObservedObject var soundManager: SoundManager
    @ObservedObject var soundTrigger = SoundTrigger.shared
    
    // Local state for hover/interactions
    @State private var isHovered: Bool = false
    @State private var showBindings: Bool = false
    
    // Binding Editing State (Local to this slot's popover/view)
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
        let isPlaying = soundManager.activeInstanceIds.contains(instance.id)
        let isLoading = soundManager.loadingInstanceIds.contains(instance.id)
        let bindingCount = soundTrigger.bindings.filter { $0.instanceId == instance.id }.count // Filter by Instance ID
        
        VStack(spacing: 4) {
            // Header / Status
            HStack {
                // Play Status Indicator
                Circle()
                    .fill(isPlaying ? Color.green : (isLoading ? Color.orange : Color.gray.opacity(0.3)))
                    .frame(width: 8, height: 8)
                
                Spacer()
                
                // Binding Badge
                if bindingCount > 0 {
                    Text("\(bindingCount)")
                        .font(.system(size: 8, weight: .bold))
                        .padding(2)
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .clipShape(Circle())
                }
                
                // Remove Button (Small X)
                Button(action: {
                    soundManager.removeInstance(instance.id, fromBus: busId)
                }) {
                    Image(systemName: "xmark")
                        .font(.system(size: 8))
                        .foregroundColor(.gray)
                }
                .buttonStyle(.plain)
                .padding(.leading, 4)
            }
            
            Spacer()
            
            // Name
            Text(instance.filename)
                .font(.system(size: 10, weight: .medium, design: .monospaced))
                .lineLimit(2)
                .multilineTextAlignment(.center)
                .foregroundColor(.white.opacity(0.9))
            
            Spacer()
            
            // Controls
            HStack {
                Button(action: {
                    if isPlaying {
                        // Stop specific instance
                        soundManager.stopSound(instanceID: instance.id)
                    } else {
                        soundManager.playSound(instance: instance, onBus: busId)
                    }
                }) {
                    Image(systemName: isPlaying ? "stop.fill" : "play.fill")
                        .font(.system(size: 12))
                        .foregroundColor(isPlaying ? .red : .white)
                }
                .buttonStyle(.plain)
                .disabled(isLoading)
                
                Spacer()
                
                Button(action: {
                    showBindings.toggle()
                }) {
                    Image(systemName: "gearshape.fill")
                        .font(.system(size: 10))
                        .foregroundColor(showBindings ? .blue : .white.opacity(0.5))
                }
                .buttonStyle(.plain)
                .popover(isPresented: $showBindings) {
                    bindingEditor
                        .frame(width: 250, height: 300)
                }
            }
        }
        .padding(6)
        .frame(width: 100, height: 90)
        .background(
            RoundedRectangle(cornerRadius: 6)
                .fill(Color(white: 0.15))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 6)
                .stroke(isPlaying ? Color.green : (isHovered ? Color.white.opacity(0.3) : Color.white.opacity(0.1)), lineWidth: 1)
        )
        .onHover { hover in isHovered = hover }
        .help("Sound: \(instance.filename)\nInstance: \(instance.id)")
    }
    
    var bindingEditor: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Bindings for \(instance.filename)")
                .font(.headline)
                .padding(.top)
            
            Divider()
            
            // List Existing Bindings
            let bindings = soundTrigger.bindings.filter { $0.instanceId == instance.id }
            ScrollView {
                VStack(spacing: 4) {
                    if bindings.isEmpty {
                        Text("No bindings")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    } else {
                        ForEach(bindings) { binding in
                            HStack {
                                Image(systemName: "link")
                                    .font(.system(size: 10))
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
                                    SoundTrigger.shared.removeBinding(id: binding.id)
                                } label: {
                                    Image(systemName: "trash")
                                        .foregroundColor(.red)
                                }
                                .buttonStyle(.plain)
                            }
                            .padding(4)
                            .background(Color.black.opacity(0.1))
                            .cornerRadius(4)
                        }
                    }
                }
            }
            .frame(maxHeight: 150)
            
            Divider()
            
            // Add New Control
            VStack(alignment: .leading, spacing: 6) {
                Text("Add Trigger").font(.caption).bold()
                
                HStack {
                    if isCustomKey {
                        TextField("Key", text: $customKey)
                            .textFieldStyle(.roundedBorder)
                    } else {
                        Picker("", selection: $selectedKey) {
                            Text("Select Key").tag("")
                            ForEach(soundTrigger.knownKeys, id: \.self) { key in
                                Text(key).tag(key)
                            }
                        }
                        .labelsHidden()
                    }
                    Toggle("Custom", isOn: $isCustomKey)
                        .toggleStyle(.checkbox)
                        .labelsHidden()
                }
                
                HStack {
                    Toggle("Value Check", isOn: $isValueSpecific)
                        .toggleStyle(.switch)
                    
                    if isValueSpecific {
                        Picker("", selection: $valueType) {
                            ForEach(ValueType.allCases) { type in
                                Text(type.rawValue).tag(type)
                            }
                        }
                        .labelsHidden()
                        .frame(width: 60)
                        
                        if valueType == .string {
                            TextField("Val", text: $stringValue)
                                .textFieldStyle(.roundedBorder)
                        } else {
                            Toggle("True", isOn: $boolValue)
                                .labelsHidden()
                        }
                    }
                }
                
                Button("Add Binding") {
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
                    
                    // Add binding linked to Instance ID
                    SoundTrigger.shared.addBinding(key: key, sound: instance.filename, instanceId: instance.id, value: finalVal)
                    
                    // Reset
                    if isCustomKey { customKey = "" }
                    stringValue = ""
                }
                .disabled((isCustomKey ? customKey.isEmpty : selectedKey.isEmpty))
                .frame(maxWidth: .infinity, alignment: .trailing)
            }
        }
        .padding()
    }
}
