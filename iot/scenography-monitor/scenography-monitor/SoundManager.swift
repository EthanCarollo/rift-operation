//
//  SoundManager.swift
//  scenography-monitor
//
//  Created by eth on 21/12/2025.
//

import Foundation
import AVFoundation
import SwiftUI
import Combine

class SoundManager: NSObject, ObservableObject, AVAudioPlayerDelegate {
    static let shared = SoundManager()
    
    // Dynamic path, user selectable
    @Published var soundDirectoryURL: URL
    
    // File Node Structure for recursive view
    struct FileNode: Identifiable, Hashable {
        let id = UUID()
        let name: String
        let url: URL
        let isDirectory: Bool
        var children: [FileNode]?
    }
    
    @Published var rootNodes: [FileNode] = []
    @Published var availableSounds: [String] = []
    @Published var activeBusIds: Set<Int> = []
    
    // Routing state: Sound Filename -> Bus ID. 0 = Unassigned.
    @Published var soundRoutes: [String: Int] = [:]
    
    // Metering state: Bus ID -> Normalized Level (0.0 - 1.0)
    @Published var busLevels: [Int: Float] = [:]
    
    // Dynamic Buses with Persistence
    struct AudioBus: Identifiable, Hashable {
        let id: Int
        var name: String
        var volume: Float = 0.75
        var pan: Float = 0.5
        var isMuted: Bool = false
        var isSolo: Bool = false
    }
    
    @Published var audioBuses: [AudioBus] = [
        AudioBus(id: 1, name: "Nightmare"),
        AudioBus(id: 2, name: "Dream"),
        AudioBus(id: 3, name: "Rift"),
        AudioBus(id: 4, name: "SAS")
    ]
    
    // Available Audio Devices (Mock for now, would use CoreAudio/AVFoundation in real internal impl)
    @Published var availableOutputs: [String] = [
        "MacBook Pro Speakers",
        "External Headphones", 
        "BlackHole 16ch",
        "HDMI (LG Monitor)",
        "Scarlett 2i2 USB"
    ]
    
    private var nextBusId = 5
    
    private var audioPlayers: [Int: AVAudioPlayer] = [:]
    private let bookmarkKey = "soundDirectoryBookmark"
    private var meteringTimer: Timer?
    
    override init() {
        // Default to container docs
        let defaultURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
            .appendingPathComponent("rift-operation-sounds")
        self.soundDirectoryURL = defaultURL
        
        super.init()
        
        // Try to restore saved location
        restoreBookmark()
        
        createDirectoryIfNeeded()
        refreshSounds()
        
        // Start metering loop
        startMetering()
    }
    
    // MARK: - Directory Management
    
    func selectSoundDirectory() {
        let panel = NSOpenPanel()
        panel.canChooseFiles = false
        panel.canChooseDirectories = true
        panel.allowsMultipleSelection = false
        panel.prompt = "Select Sound Library"
        
        panel.begin { [weak self] result in
            if result == .OK, let url = panel.url {
                self?.saveBookmark(for: url)
                self?.soundDirectoryURL = url
                self?.refreshSounds()
            }
        }
    }
    
    private func saveBookmark(for url: URL) {
        do {
            let data = try url.bookmarkData(options: .withSecurityScope, includingResourceValuesForKeys: nil, relativeTo: nil)
            UserDefaults.standard.set(data, forKey: bookmarkKey)
        } catch {
            print("Failed to save bookmark: \(error)")
        }
    }
    
    private func restoreBookmark() {
        guard let data = UserDefaults.standard.data(forKey: bookmarkKey) else { return }
        
        var isStale = false
        do {
            let url = try URL(resolvingBookmarkData: data, options: .withSecurityScope, relativeTo: nil, bookmarkDataIsStale: &isStale)
            
            if isStale {
                saveBookmark(for: url) // Refresh if stale
            }
            
            if url.startAccessingSecurityScopedResource() {
                self.soundDirectoryURL = url
            }
        } catch {
            print("Failed to restore bookmark: \(error)")
        }
    }
    
    private func createDirectoryIfNeeded() {
        if soundDirectoryURL.path.contains("Containers") && !FileManager.default.fileExists(atPath: soundDirectoryURL.path) {
            try? FileManager.default.createDirectory(at: soundDirectoryURL, withIntermediateDirectories: true)
        }
    }
    
    func refreshSounds() {
        _ = soundDirectoryURL.startAccessingSecurityScopedResource()
        defer { soundDirectoryURL.stopAccessingSecurityScopedResource() }
        
        rootNodes = scanDirectory(at: soundDirectoryURL)
    }
    
    private func scanDirectory(at url: URL) -> [FileNode] {
        var nodes: [FileNode] = []
        
        do {
            let resourceKeys: [URLResourceKey] = [.isDirectoryKey, .nameKey]
            let contents = try FileManager.default.contentsOfDirectory(at: url, includingPropertiesForKeys: resourceKeys, options: [.skipsHiddenFiles])
            
            for itemURL in contents {
                let resourceValues = try itemURL.resourceValues(forKeys: Set(resourceKeys))
                let isDirectory = resourceValues.isDirectory ?? false
                let name = resourceValues.name ?? itemURL.lastPathComponent
                
                if isDirectory {
                    let children = scanDirectory(at: itemURL)
                    nodes.append(FileNode(name: name, url: itemURL, isDirectory: true, children: children.sorted { $0.name < $1.name }))
                } else {
                    if name.hasSuffix(".mp3") || name.hasSuffix(".wav") || name.hasSuffix(".m4a") {
                        nodes.append(FileNode(name: name, url: itemURL, isDirectory: false, children: nil))
                    }
                }
            }
        } catch {
            print("Error scanning directory \(url): \(error)")
        }
        
        return nodes.sorted {
            if $0.isDirectory && !$1.isDirectory { return true }
            if !$0.isDirectory && $1.isDirectory { return false }
            return $0.name < $1.name
        }
    }
    
    // Helper to get helper text for AudioBusView
    func getAssignedSound(forBus busId: Int) -> String? {
        return soundRoutes.first(where: { $0.value == busId })?.key
    }
    
    // Helper to get all files flattened (for filtering)
    func getAllFiles() -> [FileNode] {
        return flatten(nodes: rootNodes)
    }
    
    private func flatten(nodes: [FileNode]) -> [FileNode] {
        var result: [FileNode] = []
        for node in nodes {
            if node.isDirectory {
                if let children = node.children {
                    result.append(contentsOf: flatten(nodes: children))
                }
            } else {
                result.append(node)
            }
        }
        return result
    }
    
    // MARK: - Bus Management
    
    func addBus() {
        let newBus = AudioBus(id: nextBusId, name: "BUS \(nextBusId)")
        audioBuses.append(newBus)
        nextBusId += 1
    }
    
    func removeBus(id: Int) {
        audioBuses.removeAll { $0.id == id }
        stopSound(onBus: id)
    }
    
    // MARK: - Playback Control
    
    func setVolume(_ volume: Float, onBus busId: Int) {
        // Update Bus Model
        if let index = audioBuses.firstIndex(where: { $0.id == busId }) {
            audioBuses[index].volume = volume
            
            // Apply to active player if not muted
            if let player = audioPlayers[busId], !audioBuses[index].isMuted {
                player.volume = volume
            }
        }
    }
    
    func setPan(_ pan: Float, onBus busId: Int) {
        // Update Bus Model
        if let index = audioBuses.firstIndex(where: { $0.id == busId }) {
            audioBuses[index].pan = pan
            
            // Apply to active player
            if let player = audioPlayers[busId] {
                player.pan = (pan * 2.0) - 1.0 // Convert 0...1 to -1...1
            }
        }
    }
    
    func toggleMute(onBus busId: Int) {
        if let index = audioBuses.firstIndex(where: { $0.id == busId }) {
            audioBuses[index].isMuted.toggle()
            let isMuted = audioBuses[index].isMuted
            let volume = audioBuses[index].volume
            
            if let player = audioPlayers[busId] {
                player.volume = isMuted ? 0 : volume
            }
            updateSoloState() // Re-check solo logic as mute overrides
        }
    }
    
    func toggleSolo(onBus busId: Int) {
        if let index = audioBuses.firstIndex(where: { $0.id == busId }) {
            audioBuses[index].isSolo.toggle()
            updateSoloState()
        }
    }
    
    private func updateSoloState() {
        let anySolo = audioBuses.contains { $0.isSolo }
        
        for index in audioBuses.indices {
            let bus = audioBuses[index]
            let player = audioPlayers[bus.id]
            
            if anySolo {
                // Should only play if THIS bus is solod
                if bus.isSolo {
                    // It is solo, play at volume (unless locally muted)
                    if let player = player {
                        player.volume = bus.isMuted ? 0 : bus.volume
                    }
                } else {
                    // Not solo, silence it
                    if let player = player {
                        player.volume = 0
                    }
                }
            } else {
                // No solo active, respect local mute
                if let player = player {
                    player.volume = bus.isMuted ? 0 : bus.volume
                }
            }
        }
    }
    
    func playSound(node: FileNode, onBus busId: Int) {
        // 1. Update Route
        soundRoutes[node.name] = busId
        
        // 2. Play
        stopSound(onBus: busId)
        
        let url = node.url
        do {
            let player = try AVAudioPlayer(contentsOf: url)
            player.delegate = self
            
            // Apply Bus Settings
            if let bus = audioBuses.first(where: { $0.id == busId }) {
                // Volume logic factoring in Mute and Solo
                let anySolo = audioBuses.contains { $0.isSolo }
                var targetVolume = bus.volume
                
                if bus.isMuted {
                    targetVolume = 0
                } else if anySolo && !bus.isSolo {
                    targetVolume = 0
                }
                
                player.volume = targetVolume
                player.pan = (bus.pan * 2.0) - 1.0
            } else {
                // Fallback default
                player.volume = 0.75
                player.pan = 0.0
            }
            
            player.numberOfLoops = -1 // Loop indefinitely
            player.isMeteringEnabled = true
            if player.play() {
                audioPlayers[busId] = player
                activeBusIds.insert(busId)
                print("Playing \(node.name) on Bus \(busId)")
            } else {
                print("Failed to play player for \(node.name)")
            }
            
            // Ensure timer is running
            if meteringTimer == nil {
                startMetering()
            }
            
        } catch {
            print("Playback failed: \(error)")
        }
    }
    
    func stopSound(onBus busId: Int) {
        if let player = audioPlayers[busId] {
            player.stop()
            audioPlayers.removeValue(forKey: busId)
            activeBusIds.remove(busId)
            busLevels[busId] = 0 // Reset meter
        }
    }
    
    func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        if let (busId, _) = audioPlayers.first(where: { $0.value === player }) {
            audioPlayers.removeValue(forKey: busId)
            activeBusIds.remove(busId)
            busLevels[busId] = 0
        }
    }
    
    // MARK: - Metering
    
    private func startMetering() {
        meteringTimer?.invalidate()
        meteringTimer = Timer.scheduledTimer(withTimeInterval: 0.05, repeats: true) { [weak self] _ in
            self?.updateMeters()
        }
    }
    
    private func updateMeters() {
        guard !activeBusIds.isEmpty else { return }
        
        for (busId, player) in audioPlayers {
            if player.isPlaying {
                player.updateMeters()
                let power = player.averagePower(forChannel: 0)
                let level = max(0.0, (power + 60) / 60)
                busLevels[busId] = level
            } else {
                busLevels[busId] = 0.0
            }
        }
    }
    
    func refreshAudioDevices() {
        // In a real app, this would query CoreAudio. 
        // For now, we just simulate a refresh or keep static list.
        objectWillChange.send()
        print("Refreshing Audio Devices...")
    }
}
