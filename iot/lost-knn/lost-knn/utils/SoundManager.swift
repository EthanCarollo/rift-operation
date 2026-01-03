//
//  SoundManager.swift
//  lost-knn
//
//  Created by Tom Boullay on 03/01/2025
//

import SwiftUI
import AVFoundation
import Combine

class SoundManager: NSObject, ObservableObject, AVAudioPlayerDelegate {
    @Published var availableSounds: [String] = []
    @Published var currentlyPlaying: String?
    private var audioPlayer: AVAudioPlayer?
    
    override init() {
        super.init()
        listSounds()
        setupObservers()
    }
    
    private func setupObservers() {
        NotificationCenter.default.addObserver(forName: Notification.Name("PlaySoundNotification"), object: nil, queue: .main) { [weak self] notification in
            if let filename = notification.userInfo?["filename"] as? String {
                self?.playSound(named: filename)
            }
        }
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
    
    func listSounds() {
        let fileManager = FileManager.default
        if let resourcePath = Bundle.main.resourcePath {
             do {
                 let items = try fileManager.contentsOfDirectory(atPath: resourcePath)
                 let sounds = items.filter { $0.hasSuffix(".mp3") || $0.hasSuffix(".wav") }
                 self.availableSounds = sounds.sorted()
                 // Also try looking specifically in a "sounds" subdirectory if it exists as a folder reference
                 let soundsPath = (resourcePath as NSString).appendingPathComponent("sounds")
                 if fileManager.fileExists(atPath: soundsPath) {
                     let subItems = try fileManager.contentsOfDirectory(atPath: soundsPath)
                     let subSounds = subItems.filter { $0.hasSuffix(".mp3") || $0.hasSuffix(".wav") }
                     self.availableSounds.append(contentsOf: subSounds)
                 }
                 
             } catch {
                 print("Error listing sounds: \(error)")
             }
        }
    }
    
    func playSound(named filename: String) {
        var soundURL: URL?
        // Try simple filename lookup
        if let url = Bundle.main.url(forResource: filename, withExtension: nil) {
            soundURL = url
        } else {
            // Try in sounds/ subdir
            if let resourcePath = Bundle.main.resourcePath {
                let path = (resourcePath as NSString).appendingPathComponent("sounds/\(filename)")
                if FileManager.default.fileExists(atPath: path) {
                    soundURL = URL(fileURLWithPath: path)
                }
            }
        }
        
        guard let url = soundURL else {
            print("Sound file not found: \(filename)")
            return
        }
        
        do {
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .default)
            try AVAudioSession.sharedInstance().setActive(true)
            
            audioPlayer = try AVAudioPlayer(contentsOf: url)
            audioPlayer?.delegate = self
            audioPlayer?.play()
            
            DispatchQueue.main.async {
                self.currentlyPlaying = filename
            }
            
            print("Playing: \(filename)")
        } catch {
            print("Playback failed: \(error)")
        }
    }
    
    // MARK: - AVAudioPlayerDelegate
    func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        DispatchQueue.main.async {
            self.currentlyPlaying = nil
        }
    }
}
