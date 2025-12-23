//
//  BindingEditorSheet.swift
//  scenography-monitor
//
//  Created by eth on 22/12/2025.
//

import SwiftUI

struct BindingEditorSheet: View {
    let soundName: String
    @Binding var isPresented: Bool
    @ObservedObject var soundTrigger = SoundTrigger.shared
    
    // New Binding State
    @State private var selectedKey: String = ""
    @State private var targetValue: String = ""
    @State private var isCustomKey: Bool = false
    @State private var customKey: String = ""
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("BINDINGS: \(soundName)")
                    .font(.system(size: 12, weight: .bold, design: .monospaced))
                    .foregroundColor(.secondary)
                Spacer()
                Button("Done") { isPresented = false }
                    .controlSize(.small)
            }
            .padding()
            .background(Color(nsColor: .controlBackgroundColor))
            
            // Add New Binding Section
            VStack(alignment: .leading, spacing: 10) {
                Text("Add New Trigger")
                    .font(.headline)
                
                HStack {
                    if isCustomKey {
                        TextField("JSON Key", text: $customKey)
                            .textFieldStyle(.roundedBorder)
                    } else {
                        Picker("Key", selection: $selectedKey) {
                            Text("Select Key...").tag("")
                            ForEach(soundTrigger.knownKeys, id: \.self) { key in
                                Text(key).tag(key)
                            }
                        }
                        .labelsHidden() // We use our own label or placeholder
                    }
                    
                    Toggle("Custom", isOn: $isCustomKey)
                        .toggleStyle(.checkbox)
                        .font(.caption)
                }
                
                HStack {
                    TextField("Target Value (Optional)", text: $targetValue)
                        .textFieldStyle(.roundedBorder)
                    
                    Button("Add") {
                        let finalKey = isCustomKey ? customKey : selectedKey
                        guard !finalKey.isEmpty else { return }
                        let finalValue = targetValue.isEmpty ? nil : targetValue
                        
                        SoundTrigger.shared.addBinding(key: finalKey, sound: soundName, instanceId: UUID(), value: finalValue)
                        
                        // Reset
                        if isCustomKey { customKey = "" }
                        targetValue = ""
                    }
                    .disabled((isCustomKey ? customKey.isEmpty : selectedKey.isEmpty))
                }
                
                Text("Leave Value empty to trigger on any change.")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(nsColor: .windowBackgroundColor))
            
            Divider()
            
            // List of Existing Bindings
            let bindings = soundTrigger.bindings.filter { $0.soundName == soundName }
            
            if bindings.isEmpty {
                 VStack(spacing: 12) {
                     Spacer()
                     Image(systemName: "link.badge.plus")
                         .font(.largeTitle)
                         .foregroundColor(.secondary.opacity(0.3))
                     Text("No bindings configured.")
                         .foregroundColor(.secondary)
                     Spacer()
                 }
                 .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                List {
                    ForEach(bindings) { binding in
                        HStack {
                            VStack(alignment: .leading) {
                                Text(binding.jsonKey)
                                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                                
                                if let val = binding.targetValue {
                                    Text("== \(val)")
                                        .font(.system(size: 10, design: .monospaced))
                                        .foregroundColor(.blue)
                                } else {
                                    Text("(Any Change)")
                                        .font(.system(size: 10, design: .monospaced))
                                        .foregroundColor(.green)
                                }
                            }
                            
                            Spacer()
                            
                            Button(action: {
                                SoundTrigger.shared.removeBinding(id: binding.id)
                            }) {
                                Image(systemName: "trash")
                                    .foregroundColor(.red)
                            }
                            .buttonStyle(.plain)
                        }
                        .padding(.vertical, 4)
                    }
                }
                .listStyle(.plain)
            }
        }
        .frame(width: 400, height: 400)
    }
}
