import Foundation
import Combine
import SwiftUI

class SoundTrigger: ObservableObject {
    static let shared = SoundTrigger()
    
    // Configuration Binding
    struct BindingConfig: Identifiable, Hashable, Codable {
        let id: UUID
        let jsonKey: String
        let soundName: String // Keep for display/fallback
        var instanceId: UUID? // Optional for migration, but enforced for new bindings
        let targetValue: String? 
        
        init(id: UUID = UUID(), jsonKey: String, soundName: String, instanceId: UUID? = nil, targetValue: String?) {
            self.id = id
            self.jsonKey = jsonKey
            self.soundName = soundName
            self.instanceId = instanceId
            self.targetValue = targetValue
        }
    }
    
    @Published var bindings: [BindingConfig] = []
    
    private var lastValues: [String: Any] = [:]
    private var cancellables = Set<AnyCancellable>()
    private var lastTriggerTimes: [String: Date] = [:]
    
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
            .dropFirst() // Ignore initial empty state?
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
                    let matchesTarget = (currentStr == targetStr)
                    
                    // Logic: Trigger if matches target AND:
                    // 1. Value CHANGED from last time
                    // 2. OR Value is SAME but enough time passed (Replay)
                    
                    let lastRaw = lastValues[binding.jsonKey]
                    let lastStr = lastRaw != nil ? normalize(lastRaw!) : nil
                    let changed = (currentStr != lastStr)
                    
                    let now = Date()
                    let timeSinceLast = now.timeIntervalSince(lastTriggerTimes[binding.jsonKey] ?? .distantPast)
                    let isReplay = matchesTarget && !changed && timeSinceLast > 0.3 // 300ms debounce for replay
                    
                    if matchesTarget && (changed || isReplay) {
                         shouldTrigger = true
                         // print("SoundTrigger: MATCH! Key=\(binding.jsonKey) Val=\(currentStr) (Replay: \(isReplay))")
                    }
                } else {
                    // Boolean/Existence matching (Old behavior - preserved but improved)
                    let isTrigger = isTruthy(rawValue)
                    let lastValue = lastValues[binding.jsonKey]
                    let wasTrigger = isTruthy(lastValue)
                    
                    // Also allow replay for boolean triggers?
                    let now = Date()
                    let timeSinceLast = now.timeIntervalSince(lastTriggerTimes[binding.jsonKey] ?? .distantPast)
                    let isReplay = isTrigger && (isTrigger == wasTrigger) && timeSinceLast > 0.3
                    
                    if isTrigger && (!wasTrigger || isReplay) {
                        shouldTrigger = true
                    }
                }
                
                if shouldTrigger {
                    print("Triggering Sound for \(binding.jsonKey) [Val: \(rawValue)]")
                    triggerSound(binding)
                    lastTriggerTimes[binding.jsonKey] = Date()
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
            // New Instance Logic
            if let instanceId = binding.instanceId {
                // Find instance in buses
                for (busId, instances) in SoundManager.shared.busSamples {
                    if let instance = instances.first(where: { $0.id == instanceId }) {
                        SoundManager.shared.playSound(instance: instance, onBus: busId)
                        return
                    }
                }
                print("SoundTrigger: Instance \(instanceId) not found in any bus.")
            } else {
                // FALLBACK: Old SoundName logic (Temporary)
                // We should eventually remove this.
                print("SoundTrigger: Binding has no instance ID (Old Format).")
            }
        }
    }

    // Public API to manage bindings
    func addBinding(key: String, sound: String, instanceId: UUID, value: String? = nil) {
        // Allow multiple bindings for same key IF they have different values
        // But remove exact duplicates
        bindings.removeAll { $0.jsonKey == key && $0.targetValue == value && $0.instanceId == instanceId }
        
        let binding = BindingConfig(jsonKey: key, soundName: sound, instanceId: instanceId, targetValue: value)
        bindings.append(binding)
        print("Bound '\(key)' (Val: \(value ?? "Any")) to instance '\(instanceId)'")
    }
    
    func removeBindings(forInstance instanceId: UUID) {
        bindings.removeAll { $0.instanceId == instanceId }
        print("Removed all bindings for instance '\(instanceId)'")
    }
    
    // Deprecated sound-name based removal
    func removeBindings(forSound soundName: String) {
        bindings.removeAll { $0.soundName == soundName }
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
