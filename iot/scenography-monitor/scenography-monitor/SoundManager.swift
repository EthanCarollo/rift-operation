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
        
        // Start metering loop (could be optimized to only run when playing)
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
                // Note context: security scoped resources need to be stopped when done, usually.
                // For a long-running app watching a folder, we keep it open?
                // Or stop/start on access? For now, we keep logic simple. Use startAccessing when enumerating?
            }
        } catch {
            print("Failed to restore bookmark: \(error)")
        }
    }
    
    private func createDirectoryIfNeeded() {
        // Only create if it's the default container path, otherwise assume user manages it
        if soundDirectoryURL.path.contains("Containers") && !FileManager.default.fileExists(atPath: soundDirectoryURL.path) {
            try? FileManager.default.createDirectory(at: soundDirectoryURL, withIntermediateDirectories: true)
        }
    }
    
    func refreshSounds() {
        // Ensure we have access if it's a security scoped URL
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
    
    // MARK: - Playback Control
    
    func setVolume(_ volume: Float, onBus busId: Int) {
        audioPlayers[busId]?.volume = volume
    }
    
    func setPan(_ pan: Float, onBus busId: Int) {
        audioPlayers[busId]?.pan = pan
    }
    
    func playSound(node: FileNode, onBus busId: Int, volume: Float = 1.0, pan: Float = 0.0) {
        stopSound(onBus: busId)
        soundRoutes[node.name] = busId
        
        do {
            // Need access if file is in security scoped dir?
            // Usually parent access grants child access, but let's be safe.
            // Actually, if we hold the parent securely, we can read children.
            // But checking...
            let player = try AVAudioPlayer(contentsOf: node.url)
            player.delegate = self
            player.volume = volume
            player.pan = pan
            player.isMeteringEnabled = true // Enable metering
            player.prepareToPlay()
            player.play()
            audioPlayers[busId] = player
            activeBusIds.insert(busId)
            
            // Ensure timer is running
            if meteringTimer == nil {
                startMetering()
            }
        } catch {
            print("Error playing sound \(node.name): \(error)")
        }
    }
    
    func stopSound(onBus busId: Int) {
        audioPlayers[busId]?.stop()
        audioPlayers[busId] = nil
        activeBusIds.remove(busId)
        busLevels[busId] = 0.0 // Reset meter
    }
    
    func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        if let (busId, _) = audioPlayers.first(where: { $0.value === player }) {
            audioPlayers[busId] = nil
            activeBusIds.remove(busId)
            busLevels[busId] = 0.0 // Reset meter
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
        guard !activeBusIds.isEmpty else {
            // Optional: stop timer if empty? keeping it simple for now.
            return
        }
        
        for (busId, player) in audioPlayers {
            if player.isPlaying {
                player.updateMeters()
                // Average power is usually -160 to 0 dB
                // Normalize 0.0 to 1.0
                let power = player.averagePower(forChannel: 0)
                let level = max(0.0, (power + 60) / 60) // Simple normalization from -60dB
                busLevels[busId] = level
            } else {
                busLevels[busId] = 0.0
            }
        }
    }
}
