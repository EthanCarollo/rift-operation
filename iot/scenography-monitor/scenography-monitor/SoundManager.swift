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
        
        init(id: UUID = UUID(), filename: String) {
            self.id = id
            self.filename = filename
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
    
    @Published var soundRoutes: [String: Int] = [:] // Backwards compatibility mock if needed, but better to remove usage.

    @Published var activeInstanceIds: Set<UUID> = []

    @Published var loadingInstanceIds: Set<UUID> = []
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
                let hue = Double(i) * 0.15
                let sat = 0.4
                let bri = 0.7
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
            // Stop all playing instances on this bus
            let instances = busSamples[busId] ?? []
            for instance in instances {
                if let player = players[instance.id], player.isPlaying {
                    stopSound(instanceID: instance.id)
                    print("Output changed for Bus \(busId). Stopped \(instance.filename).")
                }
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
        
        player.scheduleFile(file, at: nil) { [weak self] in
            DispatchQueue.main.async {
                guard let self = self else { return }
                if self.activeInstanceIds.contains(instance.id) {
                     self.activeInstanceIds.remove(instance.id)
                     // self.busLevels[busId] = 0 // Don't reset bus level, others might be playing
                     print("Playback finished naturally for \(instance.filename)")
                }
            }
        }
        
        player.installTap(onBus: 0, bufferSize: 1024, format: file.processingFormat) { [weak self] (buf, time) in
             self?.processMeter(buffer: buf, busId: busId)
        }
        
        // Initial Volume/Pan
        // We need to fetch it safely. Since we are in Graph Queue, we can't access Main Actor 'audioBuses'.
        // But we can just trigger an update or default to 1.0 then update.
        // Or wait, we are about to play. Let's play then update.
        
        do {
            if !engine.isRunning { try engine.start() }
            player.play()
            
            players[instance.id] = player
            
            DispatchQueue.main.async {
                self.activeInstanceIds.insert(instance.id)
                self.loadingInstanceIds.remove(instance.id)
                // Trigger volume update now that player exists
                self.updatePlayerVolume(busId)
            }
            
            print("Playing \(instance.id) (\(instance.filename)) on Bus \(busId)")
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
    func setOutputDevice(uid: String, name: String, onBus busId: Int) {
        guard let index = audioBuses.firstIndex(where: { $0.id == busId }) else { return }
        
        // Update Bus Data on Main
        DispatchQueue.main.async {
            self.audioBuses[index].outputDeviceUID = uid
            self.audioBuses[index].outputDeviceName = name
        }
    }
    
    func selectOutput(name: String, forBus busId: Int) {
        // Find device by name
        if let device = availableOutputDevices.first(where: { $0.name == name }) {
            setOutputDevice(uid: device.uid, name: device.name, onBus: busId)
        }
    }
}
