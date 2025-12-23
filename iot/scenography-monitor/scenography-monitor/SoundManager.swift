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
import Combine
import CoreAudio
import Accelerate

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
    // Polling Model: Raw data buffer accessed by Main Thread Timer

    private var rawBusLevels: [Int: Float] = [:] 
    private let meterLock = NSLock() 
    
    // UI Update Timer
    private var uiUpdateTimer: Timer?

    
    // Serial queue for all Audio Engine graph mutations to prevent Main Thread blocking
    private let audioGraphQueue = DispatchQueue(label: "com.rift.audioGraph", qos: .userInitiated)
    
    override init() {
        let defaultURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
            .appendingPathComponent("rift-operation-sounds")
        self.soundDirectoryURL = defaultURL
        
        super.init()
        
        // Initialize 12 Fixed Buses
        for i in 1...12 {
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
        
        // Ensure the graph has a valid mixer-to-output connection by accessing mainMixerNode
        _ = engine.mainMixerNode
        
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
        audioGraphQueue.async { [weak self] in
            guard let self = self, let player = self.players[busId] else { return }
            
            // Access bus config on Main Thread (snapshotting)
            // Wait, we are on background queue. We can't access self.audioBuses unsafely if it's main-thread isolated.
            // Correct pattern: Capture values on caller side (Main Thread) pass to background closure.
            // However, updatePlayerVolume is called from seemingly anywhere.
            // Let's rely on atomic/safe dispatch back to main to read properties? No, that's circular.
            // BETTER: Pass volume/pan as arguments to this function, or Assume self.audioBuses is thread safe?
            // self.audioBuses is @Published.
            
            // RE-FACTOR: We need to get the config on Main, then dispatch.
            // Since this method logic is complex (solo/mute), let's grab state on main then dispatch.
            
            DispatchQueue.main.async {
                guard let bus = self.audioBuses.first(where: { $0.id == busId }) else { return }
                let anySolo = self.audioBuses.contains { $0.isSolo }
                
                var targetVolume = bus.volume
                if bus.isMuted {
                    targetVolume = 0
                } else if anySolo && !bus.isSolo {
                    targetVolume = 0
                }
                let targetPan = (bus.pan * 2.0) - 1.0
                
                self.audioGraphQueue.async {
                    // Check if player still exists
                    if let player = self.players[busId] {
                        player.volume = targetVolume
                        player.pan = targetPan
                    }
                }
            }
        }
    }
    
    // Updates volume directly on the player without triggering a full UI/Persistence update via @Published
    func previewVolume(_ volume: Float, onBus busId: Int) {
        // Fast path for dragging
        // Capture logic state on Main (assuming this is called from UI)
        let anySolo = audioBuses.contains { $0.isSolo }
        var targetVolume = volume
        
        // We need 'bus' state.
        guard let bus = audioBuses.first(where: { $0.id == busId }) else { return }
        
        if bus.isMuted {
            targetVolume = 0
        } else if anySolo && !bus.isSolo {
            targetVolume = 0
        }
        
        audioGraphQueue.async { [weak self] in
            if let player = self?.players[busId] {
                player.volume = targetVolume
            }
        }
    }
    
    // Updates pan directly on the player without triggering a full UI/Persistence update via @Published
    func previewPan(_ pan: Float, onBus busId: Int) {
        let targetPan = (pan * 2.0) - 1.0
        audioGraphQueue.async { [weak self] in
            if let player = self?.players[busId] {
                player.pan = targetPan
            }
        }
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
                
                // Dispatch back to Graph Queue for Engine Operations
                // Streaming Mode: No heavy buffer read here.
                
                self.audioGraphQueue.async { [weak self] in
                    guard let self = self else { return }
                    
                    DispatchQueue.main.async {
                        if self.soundRoutes[node.name] == busId {
                            // Route confirmed. Now execute Graph mutation on Graph Queue
                            self.audioGraphQueue.async {
                                self.finalizePlayback(file: file, busId: busId, outputUID: outputDeviceUID, outputName: outputDeviceName, nodeName: node.name)
                            }
                        } else {
                            print("Playback cancelled for \(node.name) - Route changed during load")
                        }
                    }
                }
                
            } catch {
                print("Async Load failed for \(node.name): \(error)")
            }
        }
    }
    
    // Internal helper running on Main Thread
    private func finalizePlayback(file: AVAudioFile, busId: Int, outputUID: String, outputName: String, nodeName: String) {
        let engine = getEngine(for: outputUID)
        let player = AVAudioPlayerNode()
        
        engine.attach(player)
        
        // Track the file for potential looping logic
        activeFiles[busId] = file
        
        // Connect with explicit format
        engine.connect(player, to: engine.mainMixerNode, format: file.processingFormat)
        
        // Loop Logic - Disabled as per user request (Single play)
        // Add completion handler to reset UI state when finished
        player.scheduleFile(file, at: nil) { [weak self] in
            DispatchQueue.main.async {
                guard let self = self else { return }
                
                // Only remove if we haven't already stopped (to avoid race with manual stop UI flicker?)
                // Actually, if it finishes naturally, we just remove it.
                // Reset Level visually too.
                if self.activeBusIds.contains(busId) {
                     self.activeBusIds.remove(busId)
                     self.busLevels[busId] = 0
                     print("Playback finished naturally on Bus \(busId)")
                }
            }
        }
        
        // Install Tap for Metering
        player.installTap(onBus: 0, bufferSize: 1024, format: file.processingFormat) { [weak self] (buf, time) in
             self?.processMeter(buffer: buf, busId: busId)
        }
        
        // Apply Initial Bus Settings (Volume, Pan, etc.)
        updatePlayerVolume(busId)
        
        do {
            if !engine.isRunning { try engine.start() }
            player.play()
            
            players[busId] = player
            
            DispatchQueue.main.async {
                self.activeBusIds.insert(busId)
            }
            
            print("Playing \(nodeName) on Bus \(busId) via \(outputName)")
        } catch {
             print("Engine/Play failed for \(nodeName): \(error)")
        }
    }
    
    func stopSound(onBus busId: Int) {
        audioGraphQueue.async { [weak self] in
            guard let self = self else { return }
            
            if let player = self.players[busId] {
                player.stop()
                player.removeTap(onBus: 0)
                
                if let engine = player.engine {
                    engine.disconnectNodeOutput(player)
                    engine.detach(player)
                }
                
                self.players.removeValue(forKey: busId)
                self.activeFiles.removeValue(forKey: busId)
                
                DispatchQueue.main.async {
                    self.busLevels[busId] = 0
                    self.activeBusIds.remove(busId)
                }
            }
        }
    }
    
    // MARK: - Metering Logic
    private func processMeter(buffer: AVAudioPCMBuffer, busId: Int) {
        guard let channelData = buffer.floatChannelData else { return }
        let channelDataValue = channelData.pointee
        let frames = vDSP_Length(buffer.frameLength)
        
        var rms: Float = 0
        vDSP_rmsqv(channelDataValue, 1, &rms, frames)
        
        // Boost for visual
        let currentLevel = rms * 5.0
        
        // Lock-protected write (Low Overhead)
        meterLock.lock()
        rawBusLevels[busId] = currentLevel
        meterLock.unlock()
    }
    
    private func startMetering() {
        // Main Thread Timer - 30 FPS Refresh of all buses
        uiUpdateTimer = Timer.scheduledTimer(withTimeInterval: 0.032, repeats: true) { [weak self] _ in
            self?.updateBusLevels()
        }
    }
    
    private func updateBusLevels() {
        // Snapshot raw levels
        var snapshot: [Int: Float] = [:]
        meterLock.lock()
        snapshot = self.rawBusLevels
        meterLock.unlock()
        
        // Batch update UI
        for (busId, rawLevel) in snapshot {
            guard let bus = audioBuses.first(where: { $0.id == busId }) else { continue }
            
            let finalLevel: Float
            if bus.isMuted {
                finalLevel = 0
            } else {
                finalLevel = min(rawLevel * bus.volume, 1.0)
            }
            
            // Only update if changed significantly
            if abs((busLevels[busId] ?? 0) - finalLevel) > 0.01 {
                busLevels[busId] = finalLevel
            }
        }
    }
    

    
    // Global helper for random number loop (unused but kept for swift compatibility if needed)
    private func strideFrom(_ start: Int, to: Int, by: Int) -> StrideTo<Int> {
        return stride(from: start, to: to, by: by)
    }
}
