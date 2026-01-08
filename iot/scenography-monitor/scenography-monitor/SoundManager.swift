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
    
    // Playback state (Legacy properties removed)

    
    // Metering state: Bus ID -> Normalized Level (0.0 - 1.0)
    @Published var busLevels: [Int: Float] = [:]
    
    // Buses
    struct AudioBus: Identifiable, Hashable, Codable {
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
    
    // Instance Data Model
    struct SoundInstance: Identifiable, Codable, Hashable {
        let id: UUID
        let filename: String
        var preventReplayWhilePlaying: Bool = false  // Don't restart if already playing
        var loopEnabled: Bool = false                 // Loop until stopped
        
        init(id: UUID = UUID(), filename: String, preventReplayWhilePlaying: Bool = false, loopEnabled: Bool = false) {
            self.id = id
            self.filename = filename
            self.preventReplayWhilePlaying = preventReplayWhilePlaying
            self.loopEnabled = loopEnabled
        }
    }
    
    // Bus ID -> List of Instances
    @Published var busSamples: [Int: [SoundInstance]] = [:] 
    
    // Management Methods
    func addInstance(filename: String, toBus busId: Int) {
        let instance = SoundInstance(filename: filename)
        if var list = busSamples[busId] {
            list.append(instance)
            busSamples[busId] = list
        } else {
            busSamples[busId] = [instance]
        }
    }
    
    func removeInstance(_ instanceId: UUID, fromBus busId: Int) {
        stopSound(instanceID: instanceId)
        if var list = busSamples[busId] {
            list.removeAll { $0.id == instanceId }
            busSamples[busId] = list
        }
        // Notify Trigger System/Cleanup Bindings
        SoundTrigger.shared.removeBindings(forInstance: instanceId)
    }
    
    func updateInstance(_ instanceId: UUID, preventReplayWhilePlaying: Bool? = nil, loopEnabled: Bool? = nil) {
        for (busId, instances) in busSamples {
            if let index = instances.firstIndex(where: { $0.id == instanceId }) {
                var updated = instances[index]
                if let prevent = preventReplayWhilePlaying {
                    updated.preventReplayWhilePlaying = prevent
                }
                if let loop = loopEnabled {
                    updated.loopEnabled = loop
                }
                var list = instances
                list[index] = updated
                busSamples[busId] = list
                return
            }
        }
    }
    
    func getInstance(_ instanceId: UUID) -> SoundInstance? {
        for (_, instances) in busSamples {
            if let instance = instances.first(where: { $0.id == instanceId }) {
                return instance
            }
        }
        return nil
    }
    
    @Published var soundRoutes: [String: Int] = [:] // Backwards compatibility mock if needed, but better to remove usage.

    @Published var activeInstanceIds: Set<UUID> = []
    
    // UI Selection State
    @Published var selectedSoundURL: URL?

    @Published var loadingInstanceIds: Set<UUID> = []
    @Published var playbackProgress: [UUID: Float] = [:] // 0.0 to 1.0 progress for each playing instance
    @Published var selectedInstanceId: UUID? = nil // For Inspector
    
    // Available Audio Devices
    @Published var availableOutputs: [String] = [] // Names for UI
    private var availableOutputDevices: [AudioDeviceInput] = [] // Internal Full Objects
    
    // Engine & Player Storage
    // One Engine per Output Device UID
    private var engines: [String: AVAudioEngine] = [:]
    // One PlayerNode per Instance ID
    private var players: [UUID: AVAudioPlayerNode] = [:]
    // Files for looping logic
    private var activeFiles: [UUID: AVAudioFile] = [:]
    
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
                color = "#E0B084" // Darker Pastel Orange
            case 2: 
                name = "Nightmare"
                color = "#9CAFB7" // Darker Pastel Blue/Grey
            case 3: 
                name = "Dream"
                color = "#A8CDB4" // Darker Pastel Green
            case 4: 
                name = "Rift"
                color = "#DBA9A9" // Darker Pastel Red
            default: 
                // Generate varied darker pastels for others
                // Simplified: alternating greys if not specific?
                // NSColor check not needed if we just mock hex strings or use helper.
                // Simplified: alternating greys if not specific?
                // Or rotation:
                let colors = ["#B0C4DE", "#F4A460", "#ADD8E6", "#DDA0DD", "#8FBC8F"]
                color = colors[i % colors.count]
            }
            audioBuses.append(AudioBus(id: i, name: name, colorHex: color))
        }
        
        restoreBookmark()
        createDirectoryIfNeeded()
        refreshSounds()
        refreshAudioDevices()
        startMetering()
        setupHardwareListener()
    }

    private func setupHardwareListener() {
        var propertyAddress = AudioObjectPropertyAddress(
            mSelector: kAudioHardwarePropertyDevices,
            mScope: kAudioObjectPropertyScopeGlobal,
            mElement: kAudioObjectPropertyElementMain
        )
        
        let status = AudioObjectAddPropertyListener(
            AudioObjectID(kAudioObjectSystemObject),
            &propertyAddress,
            { (inObjectID, inNumberAddresses, inAddresses, inClientData) -> OSStatus in
                // Using a block/closure for simplicity, though a static proc is also fine.
                // Re-scan devices when hardware changes.
                DispatchQueue.main.async {
                    SoundManager.shared.refreshAudioDevices()
                    print("Hardware devices changed, refreshing list...")
                }
                return noErr
            },
            nil
        )
        
        if status != noErr {
            print("Failed to add hardware property listener: \(status)")
        }
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
    
    func renameSound(at url: URL, to newName: String) {
        let oldName = url.lastPathComponent
        
        // Ensure the new name has the original extension if the user didn't provide one
        let originalExtension = url.pathExtension
        var finalNewName = newName
        if !originalExtension.isEmpty && !newName.hasSuffix("." + originalExtension) {
            finalNewName = newName + "." + originalExtension
        }
        
        let targetURL = url.deletingLastPathComponent().appendingPathComponent(finalNewName)
        
        do {
            try FileManager.default.moveItem(at: url, to: targetURL)
            print("Renamed \(oldName) to \(finalNewName)")
            
            // Update all instances in busSamples to match the new filename
            DispatchQueue.main.async {
                for (busId, instances) in self.busSamples {
                    let updatedInstances = instances.map { instance -> SoundInstance in
                        if instance.filename == oldName {
                            return SoundInstance(id: instance.id, filename: finalNewName)
                        }
                        return instance
                    }
                    self.busSamples[busId] = updatedInstances
                }
                
                self.refreshSounds()
            }
        } catch {
            print("Failed to rename sound: \(error)")
        }
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
                    nodes.append(FileNode(name: name, url: itemURL, isDirectory: true, children: children))
                } else {
                    if name.hasSuffix(".mp3") || name.hasSuffix(".wav") || name.hasSuffix(".m4a") {
                        nodes.append(FileNode(name: name, url: itemURL, isDirectory: false, children: nil))
                    }
                }
            }
        } catch { print("scan error: \(error)") }
        
        return nodes.sorted { (n1, n2) -> Bool in
            if n1.isDirectory != n2.isDirectory {
                return n1.isDirectory // Directories first
            }
            return n1.name.localizedStandardCompare(n2.name) == .orderedAscending
        }
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
            var deviceName: Unmanaged<CFString>?
            var nameSize = UInt32(MemoryLayout<Unmanaged<CFString>?>.size)
            var nameAddr = AudioObjectPropertyAddress(mSelector: kAudioDevicePropertyDeviceNameCFString, mScope: kAudioObjectPropertyScopeGlobal, mElement: kAudioObjectPropertyElementMain)
            AudioObjectGetPropertyData(id, &nameAddr, 0, nil, &nameSize, &deviceName)
            
            // Get UID
            var deviceUID: Unmanaged<CFString>?
            var uidSize = UInt32(MemoryLayout<Unmanaged<CFString>?>.size)
            var uidAddr = AudioObjectPropertyAddress(mSelector: kAudioDevicePropertyDeviceUID, mScope: kAudioObjectPropertyScopeGlobal, mElement: kAudioObjectPropertyElementMain)
            AudioObjectGetPropertyData(id, &uidAddr, 0, nil, &uidSize, &deviceUID)
            
            let name = deviceName?.takeRetainedValue() as String? ?? "Unknown"
            let uid = deviceUID?.takeRetainedValue() as String? ?? "Unknown"
            
            // Check output channels
            var streamAddr = AudioObjectPropertyAddress(mSelector: kAudioDevicePropertyStreams, mScope: kAudioDevicePropertyScopeOutput, mElement: kAudioObjectPropertyElementMain)
            var streamSize: UInt32 = 0
            AudioObjectGetPropertyDataSize(id, &streamAddr, 0, nil, &streamSize)
            
            if streamSize > 0 {
                newDevices.append(AudioDeviceInput(id: id, name: name, uid: uid))
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
    
    func updatePlayerVolume(_ busId: Int) {
        // Snapshot Bus State on Main Thread
        DispatchQueue.main.async {
            guard let bus = self.audioBuses.first(where: { $0.id == busId }) else { return }
            let anySolo = self.audioBuses.contains { $0.isSolo }
            let instances = self.busSamples[busId] ?? []
            
            var targetVolume = bus.volume
            if bus.isMuted {
                targetVolume = 0
            } else if anySolo && !bus.isSolo {
                targetVolume = 0
            }
            let targetPan = (bus.pan * 2.0) - 1.0
            
            self.audioGraphQueue.async {
                // Update all players belonging to this bus
                for instance in instances {
                    if let player = self.players[instance.id] {
                        player.volume = targetVolume
                        player.pan = targetPan
                    }
                }
            }
        }
    }
    
    func updatePlayerPan(_ busId: Int) {
         updatePlayerVolume(busId)
    }
    
    // Updates volume directly on the player without triggering a full UI/Persistence update via @Published
    func previewVolume(_ volume: Float, onBus busId: Int) {
        // Capture logic state on Main (assuming this is called from UI)
        let anySolo = audioBuses.contains { $0.isSolo }
        var targetVolume = volume
        
        guard let bus = audioBuses.first(where: { $0.id == busId }) else { return }
        
        if bus.isMuted {
            targetVolume = 0
        } else if anySolo && !bus.isSolo {
            targetVolume = 0
        }
        
        let instances = busSamples[busId] ?? [] // Snapshot
        
        audioGraphQueue.async { [weak self] in
            guard let self = self else { return }
            for instance in instances {
                if let player = self.players[instance.id] {
                    player.volume = targetVolume
                }
            }
        }
    }
    
    // Updates pan directly on the player without triggering a full UI/Persistence update via @Published
    func previewPan(_ pan: Float, onBus busId: Int) {
        let targetPan = (pan * 2.0) - 1.0
        let instances = busSamples[busId] ?? [] // Snapshot
        
        audioGraphQueue.async { [weak self] in
            guard let self = self else { return }
            for instance in instances {
                if let player = self.players[instance.id] {
                    player.pan = targetPan
                }
            }
        }
    }
    
    // MARK: - Preview Playback (Library)
    
    private var previewPlayer: AVAudioPlayer?
    
    /// Quick preview of a sound file on default output
    func previewSound(at url: URL) {
        // Stop any existing preview
        previewPlayer?.stop()
        
        do {
            previewPlayer = try AVAudioPlayer(contentsOf: url)
            previewPlayer?.volume = 0.8
            previewPlayer?.play()
            print("Preview playing: \(url.lastPathComponent)")
        } catch {
            print("Preview failed: \(error)")
        }
    }
    
    func playSound(instance: SoundInstance, onBus busId: Int) {
        // Get File Node from Filename
        guard let node = getAllFiles().first(where: { $0.name == instance.filename }) else {
            print("File not found: \(instance.filename)")
            return
        }
    
        // Stop previous playback for THIS instance if any (re-trigger)
        stopSound(instanceID: instance.id)
        
        // Mark as loading
        DispatchQueue.main.async {
            self.loadingInstanceIds.insert(instance.id)
        }
        
        guard let bus = audioBuses.first(where: { $0.id == busId }) else { return }
        let outputDeviceUID = bus.outputDeviceUID
        let outputDeviceName = bus.outputDeviceName
        
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }
            
            do {
                let file = try AVAudioFile(forReading: node.url)
                
                self.audioGraphQueue.async {
                    self.finalizePlayback(file: file, busId: busId, instance: instance, outputUID: outputDeviceUID, outputName: outputDeviceName)
                }
            } catch {
                print("Async Load failed for \(node.name): \(error)")
                DispatchQueue.main.async {
                    self.loadingInstanceIds.remove(instance.id)
                }
            }
        }
    }
    
    // Internal helper running on Graph Queue
    private func finalizePlayback(file: AVAudioFile, busId: Int, instance: SoundInstance, outputUID: String, outputName: String) {
        let engine = getEngine(for: outputUID)
        let player = AVAudioPlayerNode()
        
        engine.attach(player)
        
        // Track file
        activeFiles[instance.id] = file
        
        engine.connect(player, to: engine.mainMixerNode, format: file.processingFormat)
        
        if instance.loopEnabled {
            // Looping: Use buffer with .loops option
            let frameCount = UInt32(file.length)
            guard let buffer = AVAudioPCMBuffer(pcmFormat: file.processingFormat, frameCapacity: frameCount) else {
                print("Failed to create buffer for looping")
                return
            }
            do {
                try file.read(into: buffer)
                player.scheduleBuffer(buffer, at: nil, options: .loops, completionHandler: nil)
            } catch {
                print("Failed to read file into buffer: \(error)")
                return
            }
        } else {
            // Normal playback - use completionCallbackType to fire AFTER playback finishes
            player.scheduleFile(file, at: nil, completionCallbackType: .dataPlayedBack) { [weak self] _ in
                guard let self = self else { return }
                print("Playback finished naturally for \(instance.filename)")
                // Properly clean up the player node to prevent memory leaks
                self.stopSound(instanceID: instance.id)
            }
        }
        
        let fileLength = file.length
        let sampleRate = file.processingFormat.sampleRate
        
        player.installTap(onBus: 0, bufferSize: 1024, format: file.processingFormat) { [weak self] (buf, time) in
            self?.processMeter(buffer: buf, busId: busId)
            
            // Calculate playback progress
            if let nodeTime = player.lastRenderTime,
               let playerTime = player.playerTime(forNodeTime: nodeTime) {
                let currentFrame = playerTime.sampleTime
                // Use modulo for looping sounds to wrap progress
                let wrappedFrame = instance.loopEnabled ? (currentFrame % Int64(fileLength)) : currentFrame
                let progress = Float(wrappedFrame) / Float(fileLength)
                DispatchQueue.main.async {
                    self?.playbackProgress[instance.id] = min(max(progress, 0), 1)
                }
            }
        }
        
        do {
            if !engine.isRunning { try engine.start() }
            player.play()
            
            players[instance.id] = player
            
            DispatchQueue.main.async {
                self.activeInstanceIds.insert(instance.id)
                self.loadingInstanceIds.remove(instance.id)
                self.updatePlayerVolume(busId)
                print("[SoundManager] Started Playing \(instance.filename). Total Active Key Count: \(self.players.count)")
            }
            
            print("Playing \(instance.id) (\(instance.filename)) on Bus \(busId) [Loop: \(instance.loopEnabled)]")
        } catch {
             print("Engine/Play failed: \(error)")
             DispatchQueue.main.async {
                self.loadingInstanceIds.remove(instance.id)
             }
        }
    }
    
    func stopSound(instanceID: UUID) {
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            self.activeInstanceIds.remove(instanceID)
            self.playbackProgress.removeValue(forKey: instanceID)
        }
        
        audioGraphQueue.async { [weak self] in
            guard let self = self else { return }
            
            if let player = self.players[instanceID] {
                if player.isPlaying { player.stop() }
                player.removeTap(onBus: 0)
                
                if let engine = player.engine {
                    engine.disconnectNodeOutput(player)
                    engine.detach(player)
                }
                
                self.players.removeValue(forKey: instanceID)
                self.activeFiles.removeValue(forKey: instanceID)
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
    
    // MARK: - Routing
    func selectOutput(name: String, forBus busId: Int) {
        guard let index = audioBuses.firstIndex(where: { $0.id == busId }) else { return }
        
        // Find UID from Name
        let uid: String
        if let dev = availableOutputDevices.first(where: { $0.name == name }) {
            uid = dev.uid
        } else {
            uid = "default"
        }
        
        let oldUID = audioBuses[index].outputDeviceUID
        if oldUID == uid { return }
        
        print("Switching Bus \(busId) from \(audioBuses[index].outputDeviceName) to \(name) (UID: \(uid))")
        
        // Update model immediately on main thread
        DispatchQueue.main.async {
            self.audioBuses[index].outputDeviceName = name
            self.audioBuses[index].outputDeviceUID = uid
            
            // Handle active sounds: they must be moved or stopped. 
            // Currently, we stop them to ensure a clean state on the new engine.
            let instances = self.busSamples[busId] ?? []
            for instance in instances {
                if let player = self.players[instance.id], player.isPlaying {
                    self.stopSound(instanceID: instance.id)
                    print("Output changed for Bus \(busId). Stopped \(instance.filename) for re-routing.")
                }
            }
        }
    }
}
