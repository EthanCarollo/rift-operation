//
//  SoundManager.swift
//  scenography-monitor
//
//  Created by eth on 21/12/2025.
//

import Foundation
import AVFoundation

class SoundManager: ObservableObject {
    static let shared = SoundManager()
    
    // For development, we point directly to the user's path.
    // In production, these should be in the Bundle.
    // Making this configurable or relative would be better, but for this specific task:
    let soundDirectoryPath = "/Users/ethew/Documents/Github/iotm1/iot/scenography-monitor/scenography-monitor/Sounds"
    
    @Published var availableSounds: [String] = []
    
    private var audioPlayers: [Int: AVAudioPlayer] = [:] // Map busId to player
    
    init() {
        refreshSounds()
    }
    
    func refreshSounds() {
        do {
            let items = try FileManager.default.contentsOfDirectory(atPath: soundDirectoryPath)
            availableSounds = items.filter { $0.hasSuffix(".mp3") || $0.hasSuffix(".wav") || $0.hasSuffix(".m4a") }
        } catch {
            print("Error listing sounds: \(error)")
            availableSounds = []
        }
    }
    
    func playSound(named filename: String, onBus busId: Int, volume: Float = 1.0, pan: Float = 0.0) {
        let url = URL(fileURLWithPath: soundDirectoryPath).appendingPathComponent(filename)
        
        do {
            let player = try AVAudioPlayer(contentsOf: url)
            player.volume = volume
            player.pan = pan
            player.prepareToPlay()
            player.play()
            audioPlayers[busId] = player
        } catch {
            print("Error playing sound \(filename): \(error)")
        }
    }
    
    func stopSound(onBus busId: Int) {
        audioPlayers[busId]?.stop()
        audioPlayers[busId] = nil
    }
    
    func isPlaying(onBus busId: Int) -> Bool {
        return audioPlayers[busId]?.isPlaying ?? false
    }
}
