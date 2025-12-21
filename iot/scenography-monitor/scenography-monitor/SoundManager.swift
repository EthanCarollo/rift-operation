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
    
    // Dynamic path in user documents
    var soundDirectoryURL: URL {
        FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
            .appendingPathComponent("rift-operation-sounds")
    }
    
    // File Node Structure for recursive view
    struct FileNode: Identifiable, Hashable {
        let id = UUID()
        let name: String
        let url: URL
        let isDirectory: Bool
        var children: [FileNode]?
    }
    
    @Published var rootNodes: [FileNode] = []
    @Published var activeBusIds: Set<Int> = []
    @Published var currentSoundOnBus: [Int: String] = [:] // Map busId to filename (or unique ID)
    
    private var audioPlayers: [Int: AVAudioPlayer] = [:]
    
    override init() {
        super.init()
        createDirectoryIfNeeded()
        refreshSounds()
    }
    
    private func createDirectoryIfNeeded() {
        if !FileManager.default.fileExists(atPath: soundDirectoryURL.path) {
            try? FileManager.default.createDirectory(at: soundDirectoryURL, withIntermediateDirectories: true)
        }
    }
    
    func refreshSounds() {
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
                    // Recursively scan subdirectories
                    let children = scanDirectory(at: itemURL)
                    // Only add directories if they are not empty (optional, but cleaner)
                    // letting them be empty is fine too.
                    nodes.append(FileNode(name: name, url: itemURL, isDirectory: true, children: children.sorted { $0.name < $1.name }))
                } else {
                    // Filter audio files
                    if name.hasSuffix(".mp3") || name.hasSuffix(".wav") || name.hasSuffix(".m4a") {
                        nodes.append(FileNode(name: name, url: itemURL, isDirectory: false, children: nil))
                    }
                }
            }
        } catch {
            print("Error scanning directory \(url): \(error)")
        }
        
        // Sort folders first, then files
        return nodes.sorted {
            if $0.isDirectory && !$1.isDirectory { return true }
            if !$0.isDirectory && $1.isDirectory { return false }
            return $0.name < $1.name
        }
    }
    
    func playSound(node: FileNode, onBus busId: Int, volume: Float = 1.0, pan: Float = 0.0) {
        do {
            let player = try AVAudioPlayer(contentsOf: node.url)
            player.delegate = self
            player.volume = volume
            player.pan = pan
            player.prepareToPlay()
            player.play()
            audioPlayers[busId] = player
            activeBusIds.insert(busId)
            currentSoundOnBus[busId] = node.name // Or full path if duplicates exist
        } catch {
            print("Error playing sound \(node.name): \(error)")
        }
    }
    
    func stopSound(onBus busId: Int) {
        audioPlayers[busId]?.stop()
        audioPlayers[busId] = nil
        activeBusIds.remove(busId)
        currentSoundOnBus[busId] = nil
    }
    
    func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        if let (busId, _) = audioPlayers.first(where: { $0.value === player }) {
            audioPlayers[busId] = nil
            activeBusIds.remove(busId)
            currentSoundOnBus[busId] = nil
        }
    }
}
