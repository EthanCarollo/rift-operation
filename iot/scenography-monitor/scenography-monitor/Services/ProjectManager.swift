
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
        let soundRoutes: [String: Int]
        let bindings: [SoundTrigger.BindingConfig]
        let audioBuses: [SoundManager.AudioBus]
        // Could expand to include window layout preferences etc.
        
        static var current: ProjectData {
            return ProjectData(
                version: "1.0",
                timestamp: Date(),
                soundRoutes: SoundManager.shared.soundRoutes,
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
            // Force Update Engines if needed? Actually bus settings are just data, engine logic reads them.
            // We might need to re-apply volumes to players if they are playing, but usually this is for "Loading a setup", so playback stops?
            // For now, just update data models.
            
            // Restore Routes
            SoundManager.shared.soundRoutes = projectData.soundRoutes
            
            // Restore Bindings
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
