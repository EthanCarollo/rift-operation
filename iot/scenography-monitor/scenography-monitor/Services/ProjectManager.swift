
import Foundation
import SwiftUI
import Combine
import UniformTypeIdentifiers
import Compression

// Custom UTType for .riftsceno files
extension UTType {
    static var riftsceno: UTType {
        UTType(exportedAs: "fr.riftoperation.riftsceno", conformingTo: .data)
    }
}

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
    
    // MARK: - RiftSceno Bundle Format
    
    /// Saves project as a .riftsceno bundle (ZIP with config + sounds)
    func saveRiftSceno(to url: URL) throws {
        let fm = FileManager.default
        let tempDir = fm.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try fm.createDirectory(at: tempDir, withIntermediateDirectories: true)
        defer { try? fm.removeItem(at: tempDir) }
        
        // 1. Write config.json
        let data = ProjectData.current
        let encoder = JSONEncoder()
        encoder.outputFormatting = .prettyPrinted
        encoder.dateEncodingStrategy = .iso8601
        let jsonData = try encoder.encode(data)
        let configURL = tempDir.appendingPathComponent("config.json")
        try jsonData.write(to: configURL)
        
        // 2. Copy sounds to sounds/ folder
        let soundsDir = tempDir.appendingPathComponent("sounds")
        try fm.createDirectory(at: soundsDir, withIntermediateDirectories: true)
        
        // Collect all unique filenames from busSamples
        var filenames = Set<String>()
        for (_, instances) in SoundManager.shared.busSamples {
            for instance in instances {
                filenames.insert(instance.filename)
            }
        }
        
        // Copy each sound file
        let soundLibrary = SoundManager.shared.soundDirectoryURL
        _ = soundLibrary.startAccessingSecurityScopedResource()
        defer { soundLibrary.stopAccessingSecurityScopedResource() }
        
        for filename in filenames {
            let srcURL = findSoundFile(named: filename, in: soundLibrary)
            if let srcURL = srcURL {
                let destURL = soundsDir.appendingPathComponent(filename)
                try? fm.copyItem(at: srcURL, to: destURL)
            }
        }
        
        // 3. Create ZIP archive
        try createZipArchive(from: tempDir, to: url)
        
        print("RiftSceno saved to: \(url.path)")
    }
    
    /// Loads project from a .riftsceno bundle
    func loadRiftSceno(from url: URL) throws {
        let fm = FileManager.default
        
        // Extract to app's Application Support directory
        let appSupport = fm.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
            .appendingPathComponent("RiftScenography")
        try fm.createDirectory(at: appSupport, withIntermediateDirectories: true)
        
        let projectName = url.deletingPathExtension().lastPathComponent
        let extractDir = appSupport.appendingPathComponent("Projects").appendingPathComponent(projectName)
        
        // Remove old extraction if exists
        if fm.fileExists(atPath: extractDir.path) {
            try fm.removeItem(at: extractDir)
        }
        try fm.createDirectory(at: extractDir, withIntermediateDirectories: true)
        
        // Extract ZIP
        try extractZipArchive(from: url, to: extractDir)
        
        // Load config.json
        let configURL = extractDir.appendingPathComponent("config.json")
        let configData = try Data(contentsOf: configURL)
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let projectData = try decoder.decode(ProjectData.self, from: configData)
        
        // Update sound directory to extracted sounds
        let soundsDir = extractDir.appendingPathComponent("sounds")
        if fm.fileExists(atPath: soundsDir.path) {
            DispatchQueue.main.async {
                SoundManager.shared.soundDirectoryURL = soundsDir
                SoundManager.shared.refreshSounds()
            }
        }
        
        // Restore State on Main Thread
        DispatchQueue.main.async {
            SoundManager.shared.audioBuses = projectData.audioBuses
            
            if let samples = projectData.busSamples {
                SoundManager.shared.busSamples = samples
            } else if let routes = projectData.soundRoutes {
                var newSamples: [Int: [SoundManager.SoundInstance]] = [:]
                for (soundName, busId) in routes {
                    let instance = SoundManager.SoundInstance(filename: soundName)
                    newSamples[busId, default: []].append(instance)
                }
                SoundManager.shared.busSamples = newSamples
                print("Migrated legacy project to Instance format.")
            }
            
            SoundTrigger.shared.bindings = projectData.bindings
            self.applyLoadedState()
        }
        print("RiftSceno loaded from: \(url.path)")
    }
    
    // MARK: - Legacy JSON Methods
    
    func saveProject(to url: URL) throws {
        // Check if it's a .riftsceno file
        if url.pathExtension == "riftsceno" {
            try saveRiftSceno(to: url)
            return
        }
        
        let data = ProjectData.current
        let encoder = JSONEncoder()
        encoder.outputFormatting = .prettyPrinted
        encoder.dateEncodingStrategy = .iso8601
        
        let jsonData = try encoder.encode(data)
        try jsonData.write(to: url)
        print("Project saved to: \(url.path)")
    }
    
    func loadProject(from url: URL) throws {
        // Check if it's a .riftsceno file
        if url.pathExtension == "riftsceno" {
            try loadRiftSceno(from: url)
            return
        }
        
        let data = try Data(contentsOf: url)
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        
        let projectData = try decoder.decode(ProjectData.self, from: data)
        
        DispatchQueue.main.async {
            SoundManager.shared.audioBuses = projectData.audioBuses
            
            if let samples = projectData.busSamples {
                SoundManager.shared.busSamples = samples
            } else if let routes = projectData.soundRoutes {
                var newSamples: [Int: [SoundManager.SoundInstance]] = [:]
                for (soundName, busId) in routes {
                     let instance = SoundManager.SoundInstance(filename: soundName)
                     newSamples[busId, default: []].append(instance)
                }
                SoundManager.shared.busSamples = newSamples
                print("Migrated legacy project to Instance format.")
            }
            
            SoundTrigger.shared.bindings = projectData.bindings
            self.applyLoadedState()
        }
        print("Project loaded from: \(url.path)")
    }
    
    private func applyLoadedState() {
        for bus in SoundManager.shared.audioBuses {
            SoundManager.shared.updatePlayerVolume(bus.id)
            SoundManager.shared.updatePlayerPan(bus.id)
        }
        WebSocketManager.shared.addLog("Loaded Project Configuration")
    }
    
    // MARK: - UI Helpers
    
    func openSavePanel() {
        let panel = NSSavePanel()
        panel.allowedContentTypes = [.riftsceno]
        panel.canCreateDirectories = true
        panel.nameFieldStringValue = "project.riftsceno"
        panel.message = "Save RiftSceno Project"
        
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
    
    func openLoadPanel() {
        let panel = NSOpenPanel()
        panel.allowedContentTypes = [.riftsceno, .json]
        panel.canChooseFiles = true
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = false
        panel.message = "Load RiftSceno Project"
        
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
    
    // MARK: - ZIP Helpers
    
    private func findSoundFile(named filename: String, in directory: URL) -> URL? {
        let fm = FileManager.default
        
        // Direct match
        let directURL = directory.appendingPathComponent(filename)
        if fm.fileExists(atPath: directURL.path) {
            return directURL
        }
        
        // Recursive search in subdirectories
        if let enumerator = fm.enumerator(at: directory, includingPropertiesForKeys: [.isRegularFileKey], options: [.skipsHiddenFiles]) {
            for case let fileURL as URL in enumerator {
                if fileURL.lastPathComponent == filename {
                    return fileURL
                }
            }
        }
        return nil
    }
    
    private func createZipArchive(from sourceDir: URL, to destURL: URL) throws {
        let fm = FileManager.default
        
        // Remove existing file
        if fm.fileExists(atPath: destURL.path) {
            try fm.removeItem(at: destURL)
        }
        
        // Use Process to call zip command (available on macOS)
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/zip")
        process.currentDirectoryURL = sourceDir
        process.arguments = ["-r", destURL.path, "."]
        
        try process.run()
        process.waitUntilExit()
        
        if process.terminationStatus != 0 {
            throw NSError(domain: "ProjectManager", code: 1, userInfo: [NSLocalizedDescriptionKey: "Failed to create ZIP archive"])
        }
    }
    
    private func extractZipArchive(from zipURL: URL, to destDir: URL) throws {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/unzip")
        process.arguments = ["-o", zipURL.path, "-d", destDir.path]
        
        try process.run()
        process.waitUntilExit()
        
        if process.terminationStatus != 0 {
            throw NSError(domain: "ProjectManager", code: 2, userInfo: [NSLocalizedDescriptionKey: "Failed to extract ZIP archive"])
        }
    }
}
