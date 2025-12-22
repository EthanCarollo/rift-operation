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
import CoreAudio

import UniformTypeIdentifiers

// Helper for Audio Devices
struct AudioDeviceInput: Hashable {
    let id: AudioObjectID
    let name: String
    let uid: String
}

class SoundManager: NSObject, ObservableObject {
    static let shared = SoundManager()
    
    // Dynamic path, user selectable
    @Published var soundDirectoryURL: URL
    
    // File Node Structure
    struct FileNode: Identifiable, Hashable {
        let id = UUID()
        let name: String
        let url: URL
        let isDirectory: Bool
        var children: [FileNode]?
    }
    
    @Published var rootNodes: [FileNode] = []
    
    // Routing state: Sound Filename -> Bus ID
    @Published var soundRoutes: [String: Int] = [:]
    
    // Playback state
    @Published var activeBusIds: Set<Int> = []
    
    // Metering state: Bus ID -> Normalized Level (0.0 - 1.0)
    @Published var busLevels: [Int: Float] = [:]
    
    // Buses
    struct AudioBus: Identifiable, Hashable {
        let id: Int
        var name: String
        var volume: Float = 0.75
        var pan: Float = 0.5
        var isMuted: Bool = false
        var isSolo: Bool = false
        var outputDeviceUID: String = "default"
        var outputDeviceName: String = "System/Default"
        var colorHex: String = "#F0F0F0" // Default light grey/white
    }
    
    @Published var audioBuses: [AudioBus] = []
    
    // Available Audio Devices
    @Published var availableOutputs: [String] = [] // Names for UI
    private var availableOutputDevices: [AudioDeviceInput] = [] // Internal Full Objects
    
    // Engine & Player Storage
    // One Engine per Output Device UID
    private var engines: [String: AVAudioEngine] = [:]
    // One PlayerNode per Bus ID
    private var players: [Int: AVAudioPlayerNode] = [:]
    // Files for looping logic
    private var activeFiles: [Int: AVAudioFile] = [:]
    
    private let bookmarkKey = "soundDirectoryBookmark"
    private var meteringTimer: Timer?
    
    override init() {
        let defaultURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
            .appendingPathComponent("rift-operation-sounds")
        self.soundDirectoryURL = defaultURL
        
        super.init()
        
        // Initialize 36 Fixed Buses
        for i in 1...36 {
            var name = "BUS \(i)"
            var color = "#F0F0F0" // Default
            
            switch i {
            case 1: 
                name = "SAS"
                color = "#FFD1A4" // Pastel Orange
            case 2: 
                name = "Nightmare"
                color = "#FFD1A4"
            case 3: 
                name = "Dream"
                color = "#FFD1A4"
            case 4: 
                name = "Rift"
                color = "#FFD1A4"
            default: break
            }
            audioBuses.append(AudioBus(id: i, name: name, colorHex: color))
        }
        
        restoreBookmark()
        createDirectoryIfNeeded()
        refreshSounds()
        refreshAudioDevices()
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
    
    func importSounds() {
        let panel = NSOpenPanel()
        panel.canChooseFiles = true
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = true
        panel.prompt = "Import Sounds"
        panel.message = "Choose audio files to add to your library"
        panel.allowedContentTypes = [.audio]
        
        panel.begin { [weak self] result in
            guard let self = self, result == .OK else { return }
            
            // Security Scope for Target
            let startAccess = self.soundDirectoryURL.startAccessingSecurityScopedResource()
            defer { if startAccess { self.soundDirectoryURL.stopAccessingSecurityScopedResource() } }
            
            for srcURL in panel.urls {
                let destURL = self.soundDirectoryURL.appendingPathComponent(srcURL.lastPathComponent)
                do {
                    if FileManager.default.fileExists(atPath: destURL.path) {
                        print("File already exists: \(destURL.lastPathComponent)")
                        // Optional: Could implement overwrite logic or rename here
                    } else {
                        try FileManager.default.copyItem(at: srcURL, to: destURL)
                        print("Imported: \(srcURL.lastPathComponent)")
                    }
                } catch {
                    print("Failed to import \(srcURL.lastPathComponent): \(error)")
                }
            }
            
            // Refresh list on Main Thread
            DispatchQueue.main.async {
                self.refreshSounds()
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
            if isStale { saveBookmark(for: url) }
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
        } catch { print("scan error: \(error)") }
        return nodes.sorted { ($0.isDirectory ? 0 : 1) < ($1.isDirectory ? 0 : 1) }
    }
    
    func getAssignedSound(forBus busId: Int) -> String? {
        return soundRoutes.first(where: { $0.value == busId })?.key
    }
    
    func getAllFiles() -> [FileNode] {
        return flatten(nodes: rootNodes)
    }
    
    private func flatten(nodes: [FileNode]) -> [FileNode] {
        var result: [FileNode] = []
        for node in nodes {
            if let children = node.children { result.append(contentsOf: flatten(nodes: children)) }
            else { result.append(node) }
        }
        return result
    }
    
    // MARK: - CoreAudio Device Management
    func refreshAudioDevices() {
        var propertyAddress = AudioObjectPropertyAddress(
            mSelector: kAudioHardwarePropertyDevices,
            mScope: kAudioObjectPropertyScopeGlobal,
            mElement: kAudioObjectPropertyElementMain
        )
        
        var dataSize: UInt32 = 0
        AudioObjectGetPropertyDataSize(AudioObjectID(kAudioObjectSystemObject), &propertyAddress, 0, nil, &dataSize)
        
        let deviceCount = Int(dataSize) / MemoryLayout<AudioObjectID>.size
        var deviceIDs = [AudioObjectID](repeating: 0, count: deviceCount)
        
        AudioObjectGetPropertyData(AudioObjectID(kAudioObjectSystemObject), &propertyAddress, 0, nil, &dataSize, &deviceIDs)
        
        var newDevices: [AudioDeviceInput] = []
        
        for id in deviceIDs {
            // Get Name
            var nameSize = UInt32(MemoryLayout<CFString>.size)
            var deviceName: CFString = "" as CFString
            var nameAddr = AudioObjectPropertyAddress(mSelector: kAudioDevicePropertyDeviceNameCFString, mScope: kAudioObjectPropertyScopeGlobal, mElement: kAudioObjectPropertyElementMain)
            AudioObjectGetPropertyData(id, &nameAddr, 0, nil, &nameSize, &deviceName)
            
            // Get UID
            var uidSize = UInt32(MemoryLayout<CFString>.size)
            var deviceUID: CFString = "" as CFString
            var uidAddr = AudioObjectPropertyAddress(mSelector: kAudioDevicePropertyDeviceUID, mScope: kAudioObjectPropertyScopeGlobal, mElement: kAudioObjectPropertyElementMain)
            AudioObjectGetPropertyData(id, &uidAddr, 0, nil, &uidSize, &deviceUID)
            
            // Check output channels
            var streamAddr = AudioObjectPropertyAddress(mSelector: kAudioDevicePropertyStreams, mScope: kAudioDevicePropertyScopeOutput, mElement: kAudioObjectPropertyElementMain)
            var streamSize: UInt32 = 0
            AudioObjectGetPropertyDataSize(id, &streamAddr, 0, nil, &streamSize)
            
            if streamSize > 0 {
                newDevices.append(AudioDeviceInput(id: id, name: String(deviceName), uid: String(deviceUID)))
            }
        }
        
        DispatchQueue.main.async {
            self.availableOutputDevices = newDevices
            self.availableOutputs = newDevices.map { $0.name }
        }
    }
    
    // MARK: - Engine Helpers
    private func getEngine(for uid: String) -> AVAudioEngine {
        // Reuse existing engine if available
        if let existing = engines[uid] {
            if !existing.isRunning { try? existing.start() }
            return existing
        }
        
        let engine = AVAudioEngine()
        
        // Bind to Hardware Device if not default
        // If "default", we just use standard routing of engine (system default).
        if uid != "default" {
            // Find ID from UID
            if let dev = availableOutputDevices.first(where: { $0.uid == uid }) {
                let deviceID = dev.id
                
                // Set Output Unit Device
                let outputNode = engine.outputNode
                if let audioUnit = outputNode.audioUnit {
                    var id = deviceID
                    let err = AudioUnitSetProperty(audioUnit,
                                         kAudioOutputUnitProperty_CurrentDevice,
                                         kAudioUnitScope_Global,
                                         0,
                                         &id,
                                         UInt32(MemoryLayout<AudioObjectID>.size))
                    if err != noErr {
                        print("Error setting audio unit device for UID \(uid): \(err)")
                    } else {
                        print("Successfully bound engine to device UID: \(uid)")
                    }
                }
            }
        }
        
        do {
            try engine.start()
            print("Engine started successfully for UID: \(uid)")
        } catch {
            print("Failed to start engine for UID \(uid): \(error)")
        }
        
        engines[uid] = engine
        return engine
    }
    
    // MARK: - Playback Control
    
    func setOutput(_ deviceName: String, onBus busId: Int) {
        if let index = audioBuses.firstIndex(where: { $0.id == busId }) {
            // Find UID from Name
            let uid: String
            if let dev = availableOutputDevices.first(where: { $0.name == deviceName }) {
                uid = dev.uid
            } else {
                uid = "default"
            }
            
            let oldUID = audioBuses[index].outputDeviceUID
            if oldUID == uid { return }
            
            // Update model
            audioBuses[index].outputDeviceName = deviceName
            audioBuses[index].outputDeviceUID = uid
            
            // If playing, restart on new engine
            // We need to re-route. Simple way: Stop. User restarts.
            // Or auto-restart if we store the current file node.
            // For now, strict restart.
            if let player = players[busId], player.isPlaying {
                stopSound(onBus: busId)
                print("Output changed for Bus \(busId). Please restart playback.")
            }
        }
    }
    
    func setVolume(_ volume: Float, onBus busId: Int) {
        if let index = audioBuses.firstIndex(where: { $0.id == busId }) {
            audioBuses[index].volume = volume
            updatePlayerVolume(busId)
        }
    }
    
    func setPan(_ pan: Float, onBus busId: Int) {
        if let index = audioBuses.firstIndex(where: { $0.id == busId }) {
            audioBuses[index].pan = pan
            updatePlayerVolume(busId) 
        }
    }
    
    func setBusName(_ name: String, onBus busId: Int) {
        if let index = audioBuses.firstIndex(where: { $0.id == busId }) {
            audioBuses[index].name = name
        }
    }
    
    func setBusColor(_ hex: String, onBus busId: Int) {
        if let index = audioBuses.firstIndex(where: { $0.id == busId }) {
            audioBuses[index].colorHex = hex
        }
    }
    
    func setBusColor(_ hex: String, onBuses busIds: Set<Int>) {
        for busId in busIds {
            if let index = audioBuses.firstIndex(where: { $0.id == busId }) {
                audioBuses[index].colorHex = hex
            }
        }
    }
    
    func toggleMute(onBus busId: Int) {
        if let index = audioBuses.firstIndex(where: { $0.id == busId }) {
            audioBuses[index].isMuted.toggle()
            updatePlayerVolume(busId)
            updateSoloState()
        }
    }
    
    func toggleSolo(onBus busId: Int) {
        if let index = audioBuses.firstIndex(where: { $0.id == busId }) {
            audioBuses[index].isSolo.toggle()
            updateSoloState()
        }
    }
    
    private func updateSoloState() {
        for bus in audioBuses {
            updatePlayerVolume(bus.id)
        }
    }
    
    private func updatePlayerVolume(_ busId: Int) {
        guard let player = players[busId], let bus = audioBuses.first(where: { $0.id == busId }) else { return }
        
        let anySolo = audioBuses.contains { $0.isSolo }
        var targetVolume = bus.volume
        
        if bus.isMuted {
            targetVolume = 0
        } else if anySolo && !bus.isSolo {
            targetVolume = 0
        }
        
        player.volume = targetVolume
        player.pan = (bus.pan * 2.0) - 1.0
    }
    
    // Updates volume directly on the player without triggering a full UI/Persistence update via @Published
    func previewVolume(_ volume: Float, onBus busId: Int) {
        guard let player = players[busId], let bus = audioBuses.first(where: { $0.id == busId }) else { return }
        
        // Calculate target volume using the PREVIEW volume, but respecting Mute/Solo logic
        let anySolo = audioBuses.contains { $0.isSolo }
        var targetVolume = volume
        
        if bus.isMuted {
            targetVolume = 0
        } else if anySolo && !bus.isSolo {
            targetVolume = 0
        }
        
        player.volume = targetVolume
    }
    
    func playSound(node: FileNode, onBus busId: Int) {
        // Stop previous sound immediately on Main Thread to prevent overlap
        stopSound(onBus: busId)
        soundRoutes[node.name] = busId
        
        guard let bus = audioBuses.first(where: { $0.id == busId }) else { return }
        let outputDeviceUID = bus.outputDeviceUID
        let outputDeviceName = bus.outputDeviceName
        
        // Dispatch heavy I/O to background
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }
            
            do {
                let file = try AVAudioFile(forReading: node.url)
                
                // Read entire file into buffer (Heavy Operation)
                guard let buffer = AVAudioPCMBuffer(pcmFormat: file.processingFormat, frameCapacity: AVAudioFrameCount(file.length)) else {
                    print("Failed to create buffer for \(node.name)")
                    return
                }
                
                try file.read(into: buffer)
                
                // Dispatch back to Main Thread for Engine Operations
                DispatchQueue.main.async {
                    // Re-check if bus is still valid and not stopped/replaced while loading
                    // We check if the route is still assigned to this bus for this file
                    if self.soundRoutes[node.name] == busId {
                        self.finalizePlayback(buffer: buffer, file: file, busId: busId, outputUID: outputDeviceUID, outputName: outputDeviceName, nodeName: node.name)
                    } else {
                        print("Playback cancelled for \(node.name) - Route changed during load")
                    }
                }
                
            } catch {
                print("Async Load failed for \(node.name): \(error)")
            }
        }
    }
    
    // Internal helper running on Main Thread
    private func finalizePlayback(buffer: AVAudioPCMBuffer, file: AVAudioFile, busId: Int, outputUID: String, outputName: String, nodeName: String) {
        let engine = getEngine(for: outputUID)
        let player = AVAudioPlayerNode()
        
        engine.attach(player)
        
        // Track the file for potential looping logic
        activeFiles[busId] = file
        
        // Connect with explicit format
        engine.connect(player, to: engine.mainMixerNode, format: buffer.format)
        
        // Loop Logic
        player.scheduleBuffer(buffer, at: nil, options: .loops, completionHandler: nil)
        
        // Install Tap for Metering
        player.installTap(onBus: 0, bufferSize: 1024, format: buffer.format) { [weak self] (buf, time) in
             self?.processMeter(buffer: buf, busId: busId)
        }
        
        // Apply Initial Bus Settings (Volume, Pan, etc.)
        updatePlayerVolume(busId)
        
        do {
            if !engine.isRunning { try engine.start() }
            player.play()
            
            players[busId] = player
            
            self.activeBusIds.insert(busId)
            
            print("Playing \(nodeName) on Bus \(busId) via \(outputName)")
        } catch {
             print("Engine/Play failed for \(nodeName): \(error)")
        }
    }
    
    func stopSound(onBus busId: Int) {
        if let player = players[busId] {
            player.stop()
            player.removeTap(onBus: 0)
            
            if let engine = player.engine {
                // Explicitly disconnect to ensure graph state is clean before detach
                engine.disconnectNodeOutput(player)
                engine.detach(player)
            }
            
            players.removeValue(forKey: busId)
            activeFiles.removeValue(forKey: busId)
            
            DispatchQueue.main.async {
                self.busLevels[busId] = 0
                self.activeBusIds.remove(busId)
            }
        }
    }
    
    // MARK: - Metering Logic
    private func processMeter(buffer: AVAudioPCMBuffer, busId: Int) {
        guard let channelData = buffer.floatChannelData else { return }
        let channelDataValue = channelData.pointee
        let frames = buffer.frameLength
        
        var rms: Float = 0
        // Sample every 4th frame to save CPU
        let stride = 4
        for i in strideFrom(0, to: Int(frames), by: stride) {
            let sample = channelDataValue[i]
            rms += sample * sample
        }
        rms = sqrt(rms / Float(frames / UInt32(stride)))
        
        // Scale and damp
        let currentLevel = rms * 5.0 // Boost for visual
        
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            // Apply volume influence to visual meter?
            // If muted, we see 0?
            // Ideally, yes.
            // If we access self.audioBuses here it might be racey? 
            // We are on Main Queue, so it is safe to read @Published.
            
            if let bus = self.audioBuses.first(where: { $0.id == busId }) {
                 if bus.isMuted {
                     self.busLevels[busId] = 0
                 } else {
                     self.busLevels[busId] = min(currentLevel * bus.volume, 1.0)
                 }
            }
        }
    }
    
    private func startMetering() {
        // Metering is handled by Tap + Main Queue dispatch.
        // No polling timer needed.
    }
    
    // Global helper for random number loop (unused but kept for swift compatibility if needed)
    private func strideFrom(_ start: Int, to: Int, by: Int) -> StrideTo<Int> {
        return stride(from: start, to: to, by: by)
    }
}
