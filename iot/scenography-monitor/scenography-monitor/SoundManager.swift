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
    
    // For development, we point directly to the user's path.
    let soundDirectoryPath = "/Users/ethew/Documents/Github/iotm1/iot/scenography-monitor/scenography-monitor/Sounds"
    
    @Published var availableSounds: [String] = []
    @Published var activeBusIds: Set<Int> = []
    
    private var audioPlayers: [Int: AVAudioPlayer] = [:] // Map busId to player
    
    override init() {
        super.init()
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
            player.delegate = self
            player.volume = volume
            player.pan = pan
            player.prepareToPlay()
            player.play()
            audioPlayers[busId] = player
            activeBusIds.insert(busId)
        } catch {
            print("Error playing sound \(filename): \(error)")
        }
    }
    
    func stopSound(onBus busId: Int) {
        audioPlayers[busId]?.stop()
        audioPlayers[busId] = nil
        activeBusIds.remove(busId)
    }
    
    func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        // Find which bus this player belongs to
        if let (busId, _) = audioPlayers.first(where: { $0.value === player }) {
            audioPlayers[busId] = nil
            activeBusIds.remove(busId)
        }
    }
}
