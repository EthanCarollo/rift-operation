import Foundation
import Combine
import SwiftUI

class SoundTrigger: ObservableObject {
    static let shared = SoundTrigger()
    
    // Configuration Binding
    struct BindingConfig: Identifiable, Hashable {
        let id = UUID()
        let jsonKey: String
        let soundName: String
        // Bus ID is now resolved dynamically from SoundManager
        let targetValue: String? // Helper: treats all incoming values as string for comparison
    }
    
    @Published var bindings: [BindingConfig] = []
    
    private var lastValues: [String: Any] = [:]
    private var cancellables = Set<AnyCancellable>()
    
    // Hardcoded keys from json_reference.json
    let knownKeys: [String] = [
        "operator_start_system",
        "operator_launch_close_rift_step_1",
        "operator_launch_close_rift_step_2",
        "operator_launch_close_rift_step_3",
        "stranger_state",
        "depth_state", 
        "lost_state",
        "end_system",
        "reset_system"
    ]
    
    init() {
        setupListener()
    }
    
    private func setupListener() {
        WebSocketManager.shared.$latestData
            .sink { [weak self] json in
                self?.process(json)
            }
            .store(in: &cancellables)
    }
    
    private func process(_ json: [String: Any]) {
        for binding in bindings {
            if let rawValue = json[binding.jsonKey] {
                var shouldTrigger = false
                
                if let targetStr = binding.targetValue {
                    // Value-based matching
                    let currentStr = normalize(rawValue)
                    let targetIsBool = (targetStr == "true" || targetStr == "false")
                    
                    // Specific check: If target is "true"/"false", normalize currentStr to "true"/"false" if it looks like a bool
                    // This handles cases where JSON sends 1/0 for booleans or actual booleans.
                    
                    // Check if value CHANGED to the target
                    let lastRaw = lastValues[binding.jsonKey]
                    let lastStr = lastRaw != nil ? normalize(lastRaw!) : nil
                    
                    if currentStr == targetStr && (lastStr != targetStr) {
                         shouldTrigger = true
                         print("SoundTrigger: MATCH! Key=\(binding.jsonKey) Val=\(currentStr) Target=\(targetStr)")
                    } else if currentStr != targetStr {
                        // Debugging mismatch if key matches but value doesn't
                        // print("SoundTrigger: Mismatch Key=\(binding.jsonKey) Val=\(currentStr) Target=\(targetStr)")
                    }
                } else {
                    // Boolean/Existence matching (Old behavior)
                    let isTrigger = isTruthy(rawValue)
                    let lastValue = lastValues[binding.jsonKey]
                    let wasTrigger = isTruthy(lastValue)
                    if isTrigger && !wasTrigger {
                        shouldTrigger = true
                    }
                }
                
                if shouldTrigger {
                    print("Triggering Sound for \(binding.jsonKey) [Val: \(rawValue)]")
                    triggerSound(binding)
                }
                
                // Update Cache
                lastValues[binding.jsonKey] = rawValue
            }
        }
    }
    
    private func normalize(_ value: Any) -> String {
        if let boolVal = value as? Bool {
            return boolVal ? "true" : "false"
        }
        // Handle NSNumber that might be boolean
        if let numVal = value as? NSNumber {
             if CFGetTypeID(numVal) == CFBooleanGetTypeID() {
                 return numVal.boolValue ? "true" : "false"
             }
        }
        return String(describing: value)
    }

    private func isTruthy(_ value: Any?) -> Bool {
        guard let value = value else { return false }
        if let boolVal = value as? Bool { return boolVal }
        if let intVal = value as? Int { return intVal != 0 }
        if let strVal = value as? String { return strVal.lowercased() == "true" }
        return true
    }
    
    private func triggerSound(_ binding: BindingConfig) {
        DispatchQueue.main.async {
            // Resolve Bus Dynamically on Main Thread
            guard let busId = SoundManager.shared.soundRoutes[binding.soundName], busId > 0 else {
                // print("SoundTrigger: Sound '\(binding.soundName)' is not assigned to any active bus. Skipping.")
                return
            }

            // Find File Node
            let allFiles = SoundManager.shared.getAllFiles()
            if let node = allFiles.first(where: { $0.name == binding.soundName }) {
                SoundManager.shared.playSound(node: node, onBus: busId)
            } else {
                print("SoundTrigger: File not found '\(binding.soundName)'")
            }
        }
    }

    // Public API to manage bindings
    func addBinding(key: String, sound: String, value: String? = nil) {
        // Allow multiple bindings for same key IF they have different values
        // But remove exact duplicates
        bindings.removeAll { $0.jsonKey == key && $0.targetValue == value && $0.soundName == sound }
        
        let binding = BindingConfig(jsonKey: key, soundName: sound, targetValue: value)
        bindings.append(binding)
        print("Bound '\(key)' (Val: \(value ?? "Any")) to sound '\(sound)'")
    }
    
    func removeBindings(forSound soundName: String) {
        bindings.removeAll { $0.soundName == soundName }
        print("Removed all bindings for sound '\(soundName)'")
    }
    
    func removeBinding(key: String) {
        bindings.removeAll { $0.jsonKey == key }
    }
    
    func removeBinding(id: UUID) {
        bindings.removeAll { $0.id == id }
    }
    
    func getBinding(for key: String) -> BindingConfig? {
        return bindings.first(where: { $0.jsonKey == key })
    }
}
