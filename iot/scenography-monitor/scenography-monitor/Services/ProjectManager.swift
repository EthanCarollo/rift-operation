
import Foundation
import SwiftUI
import Combine
import UniformTypeIdentifiers

// Service Class for Project Management
class ProjectManager: ObservableObject {
    static let shared = ProjectManager()
    
    // Structure representing the persistable state of the application
    struct ProjectData: Codable {
        let version: String
        let timestamp: Date
        let soundRoutes: [String: Int]? // Legacy (Optional for back-compat)
        let busSamples: [Int: [SoundManager.SoundInstance]]? // New Instance Data
        let bindings: [SoundTrigger.BindingConfig]
        let audioBuses: [SoundManager.AudioBus]
        
        static var current: ProjectData {
            return ProjectData(
                version: "2.0",
                timestamp: Date(),
                soundRoutes: nil, // We don't save legacy routes anymore
                busSamples: SoundManager.shared.busSamples,
                bindings: SoundTrigger.shared.bindings,
                audioBuses: SoundManager.shared.audioBuses
            )
        }
    }
    
    func saveProject(to url: URL) throws {
        let data = ProjectData.current
        let encoder = JSONEncoder()
        encoder.outputFormatting = .prettyPrinted
        encoder.dateEncodingStrategy = .iso8601
        
        let jsonData = try encoder.encode(data)
        try jsonData.write(to: url)
        print("Project saved to: \(url.path)")
    }
    
    func loadProject(from url: URL) throws {
        let data = try Data(contentsOf: url)
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        
        let projectData = try decoder.decode(ProjectData.self, from: data)
        
        // Restore State on Main Thread
        DispatchQueue.main.async {
            // Restore Buses (Volume, Pan, Color)
            SoundManager.shared.audioBuses = projectData.audioBuses
            
            // Restore Samples (Instances)
            if let samples = projectData.busSamples {
                // New Format
                SoundManager.shared.busSamples = samples
            } else if let routes = projectData.soundRoutes {
                // Formatting Migration: Legacy Routes -> Instances
                var newSamples: [Int: [SoundManager.SoundInstance]] = [:]
                for (soundName, busId) in routes {
                     let instance = SoundManager.SoundInstance(filename: soundName)
                     newSamples[busId, default: []].append(instance)
                }
                SoundManager.shared.busSamples = newSamples
                print("Migrated legacy project to Instance format.")
            }
            
            // Restore Bindings
            // Note: Bindings might need migration if they rely on soundName but we generated new UUIDs above.
            // If we migrated legacy routes, we generated NEW instances with NEW UUIDs.
            // Old bindings have 'soundName'. New bindings have 'instanceId'.
            // SoundTrigger.addBinding logic was: (key, sound).
            // Users will need to re-bind if they load an old project that uses old binding format?
            // Or we try to resolve?
            // For now, load raw bindings. SoundTrigger handles legacy "soundName" lookup as fallback.
            SoundTrigger.shared.bindings = projectData.bindings
            
            // Refresh logic to ensure UI and Audio Engine reflect changes
            self.applyLoadedState()
        }
        print("Project loaded from: \(url.path)")
    }
    
    private func applyLoadedState() {
        // Apply bus volumes to any active players if feasible
        for bus in SoundManager.shared.audioBuses {
            SoundManager.shared.updatePlayerVolume(bus.id)
            SoundManager.shared.updatePlayerPan(bus.id)
        }
        
        // Optional: Log success
        WebSocketManager.shared.addLog("Loaded Project Configuration")
    }
    
    // UI Helper: Open Save Panel
    func openSavePanel() {
        let panel = NSSavePanel()
        panel.allowedContentTypes = [.json]
        panel.canCreateDirectories = true
        panel.nameFieldStringValue = "config.json"
        panel.message = "Save Project Configuration"
        
        panel.begin { response in
            if response == .OK, let url = panel.url {
                do {
                    try self.saveProject(to: url)
                } catch {
                    print("Failed to save project: \(error)")
                }
            }
        }
    }
    
    // UI Helper: Open Load Panel
    func openLoadPanel() {
        let panel = NSOpenPanel()
        panel.allowedContentTypes = [.json]
        panel.canChooseFiles = true
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = false
        panel.message = "Load Project Configuration"
        
        panel.begin { response in
            if response == .OK, let url = panel.url {
                do {
                    try self.loadProject(from: url)
                } catch {
                    print("Failed to load project: \(error)")
                }
            }
        }
    }
}
