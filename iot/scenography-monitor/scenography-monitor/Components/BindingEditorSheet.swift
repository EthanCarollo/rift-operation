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
    @ObservedObject var soundManager = SoundManager.shared
    
    // New Binding State
    @State private var selectedKey: String = ""
    @State private var targetValue: String = ""
    @State private var isCustomKey: Bool = false
    @State private var customKey: String = ""
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Sound Binding Config")
                        .font(.headline)
                        .foregroundColor(.primary)
                    Text(soundName)
                        .font(.system(size: 11, design: .monospaced))
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                Button("Done") { isPresented = false }
                    .controlSize(.small)
            }
            .padding()
            .background(Color(nsColor: .windowBackgroundColor))
            .border(Color(nsColor: .separatorColor), width: 1, edges: [.bottom])
            
            ScrollView {
                VStack(spacing: 20) {
                    
                    // MARK: - Assignation Info
                    VStack(alignment: .leading, spacing: 8) {
                        SectionHeader(title: "ROUTING & OUTPUTS")
                        
                        let assignedBuses = soundManager.audioBuses.filter { bus in
                            // Safe unwrapping
                            guard let instances = soundManager.busSamples[bus.id] else { return false }
                            return instances.contains { $0.filename == soundName }
                        }
                        
                        if assignedBuses.isEmpty {
                            Text("Not assigned to any bus")
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .italic()
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .padding(.horizontal, 4)
                        } else {
                            VStack(spacing: 8) {
                                ForEach(assignedBuses) { bus in
                                    HStack {
                                        Circle()
                                            .fill(Color(hex: bus.colorHex))
                                            .frame(width: 8, height: 8)
                                        
                                        Text(bus.name)
                                            .font(.system(size: 11, weight: .bold))
                                        
                                        Spacer()
                                        
                                        HStack(spacing: 4) {
                                            Image(systemName: "speaker.wave.2.circle.fill")
                                                .font(.system(size: 10))
                                                .foregroundColor(.secondary)
                                            Text(bus.outputDeviceName)
                                                .font(.system(size: 10, design: .monospaced))
                                                .foregroundColor(.secondary)
                                        }
                                        .padding(.horizontal, 6)
                                        .padding(.vertical, 2)
                                        .background(Color.secondary.opacity(0.1))
                                        .cornerRadius(4)
                                    }
                                    .padding(8)
                                    .background(Color(nsColor: .controlBackgroundColor))
                                    .cornerRadius(8)
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 8)
                                            .stroke(Color.secondary.opacity(0.1), lineWidth: 1)
                                    )
                                }
                            }
                        }
                    }
                    
                    Divider()
                    
                    // MARK: - Add Trigger Form
                    VStack(alignment: .leading, spacing: 10) {
                        SectionHeader(title: "ADD TRIGGER")
                        
                        VStack(spacing: 12) {
                            // Key Selection
                            HStack {
                                Text("Key:")
                                    .font(.system(size: 11))
                                    .frame(width: 40, alignment: .trailing)
                                    .foregroundColor(.secondary)
                                
                                if isCustomKey {
                                    TextField("e.g. game_state", text: $customKey)
                                        .textFieldStyle(.roundedBorder)
                                } else {
                                    Picker("", selection: $selectedKey) {
                                        Text("Select Event Key...").tag("")
                                        Divider()
                                        ForEach(soundTrigger.knownKeys, id: \.self) { key in
                                            Text(key).tag(key)
                                        }
                                    }
                                    .labelsHidden()
                                    .frame(maxWidth: .infinity)
                                }
                                
                                Toggle("Custom", isOn: $isCustomKey)
                                    .toggleStyle(.button)
                                    .controlSize(.mini)
                            }
                            
                            // Value Selection
                            HStack {
                                Text("Value:")
                                    .font(.system(size: 11))
                                    .frame(width: 40, alignment: .trailing)
                                    .foregroundColor(.secondary)
                                
                                TextField("Optional (e.g. true, 1)", text: $targetValue)
                                    .textFieldStyle(.roundedBorder)
                            }
                            
                            HStack {
                                Spacer()
                                Button(action: addBinding) {
                                    Text("Add Trigger")
                                        .frame(maxWidth: .infinity)
                                }
                                .buttonStyle(.borderedProminent)
                                .controlSize(.regular)
                                .disabled(bindingKey.isEmpty)
                            }
                        }
                        .padding(12)
                        .background(Color(nsColor: .controlBackgroundColor))
                        .cornerRadius(8)
                    }
                    
                    Divider()
                    
                    // MARK: - Existing Bindings
                    VStack(alignment: .leading, spacing: 8) {
                        SectionHeader(title: "ACTIVE BINDINGS")
                        
                        let bindings = soundTrigger.bindings.filter { $0.soundName == soundName }
                        
                        if bindings.isEmpty {
                            HStack {
                                Spacer()
                                Text("No active triggers")
                                    .foregroundColor(.secondary)
                                    .font(.caption)
                                Spacer()
                            }
                            .padding(.vertical, 10)
                        } else {
                            ForEach(bindings) { binding in
                                BindingRow(binding: binding) {
                                    soundTrigger.removeBinding(id: binding.id)
                                }
                            }
                        }
                    }
                }
                .padding()
            }
        }
        .frame(width: 420, height: 550)
        .background(Color(nsColor: .textBackgroundColor))
    }
    
    // Helpers
    
    private var bindingKey: String {
        isCustomKey ? customKey : selectedKey
    }
    
    private func addBinding() {
        let key = bindingKey
        guard !key.isEmpty else { return }
        
        let val = targetValue.isEmpty ? nil : targetValue
        // Note: Logic here uses a new UUID for instanceId for now as per previous logic.
        // If we want to bind to specific placed instances rather than "sound name templates",
        // we'd need to select WHICH instance. For now we follow existing pattern.
        SoundTrigger.shared.addBinding(key: key, sound: soundName, instanceId: UUID(), value: val)
        
        if isCustomKey { customKey = "" }
        targetValue = ""
    }
}

// MARK: - Subviews

private struct SectionHeader: View {
    let title: String
    
    var body: some View {
        Text(title)
            .font(.system(size: 10, weight: .bold))
            .foregroundColor(.secondary)
            .tracking(1)
    }
}

private struct BindingRow: View {
    let binding: SoundTrigger.BindingConfig
    let onDelete: () -> Void
    
    @State private var isHovering = false
    
    var body: some View {
        HStack(spacing: 12) {
            // Icon
            ZStack {
                Circle()
                    .fill(Color.blue.opacity(0.1))
                    .frame(width: 24, height: 24)
                Image(systemName: "bolt.fill")
                    .font(.system(size: 10))
                    .foregroundColor(.blue)
            }
            
            // Info
            VStack(alignment: .leading, spacing: 2) {
                HStack(spacing: 4) {
                    Text(binding.jsonKey)
                        .font(.system(size: 12, weight: .medium, design: .monospaced))
                        .foregroundColor(.primary)
                }
                
                HStack(spacing: 4) {
                    Text("Trigger when:")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    
                    if let val = binding.targetValue {
                        Text("== \"\(val)\"")
                            .font(.system(size: 10, weight: .bold, design: .monospaced))
                            .padding(.horizontal, 4)
                            .padding(.vertical, 1)
                            .background(Color.yellow.opacity(0.2))
                            .foregroundColor(.orange)
                            .cornerRadius(3)
                    } else {
                        Text("ANY CHANGE")
                            .font(.system(size: 9, weight: .bold))
                            .padding(.horizontal, 4)
                            .padding(.vertical, 1)
                            .background(Color.green.opacity(0.1))
                            .foregroundColor(.green)
                            .cornerRadius(3)
                    }
                }
            }
            
            Spacer()
            
            Button(action: onDelete) {
                Image(systemName: "xmark")
                    .font(.system(size: 10, weight: .bold))
                    .foregroundColor(isHovering ? .red : .secondary)
                    .frame(width: 20, height: 20)
            }
            .buttonStyle(.plain)
            .onHover { isHovering = $0 }
        }
        .padding(10)
        .background(Color(nsColor: .controlBackgroundColor))
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color.secondary.opacity(0.1), lineWidth: 1)
        )
    }
}
