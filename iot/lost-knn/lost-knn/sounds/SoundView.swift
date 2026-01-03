//
//  SoundView.swift
//  lost-knn
//
//  Created by Tom Boullay on 03/01/2025
//

import SwiftUI
import Foundation

struct SoundView: View {
    @StateObject private var soundManager = SoundManager()
    
    var body: some View {
        NavigationView {
            List {
                ForEach(soundManager.availableSounds, id: \.self) { sound in
                    Button(action: {
                        if soundManager.currentlyPlaying == sound {
                            // Optional: Implement pause/stop logic here if desired, 
                            // but for now just re-triggering play usually restarts or does nothing depending on manager.
                            // User asked to change icon to pause, implying it might be pausable, 
                            // but SoundManager.playSound plays. We'll leave action as is.
                            soundManager.playSound(named: sound)
                        } else {
                            soundManager.playSound(named: sound)
                        }
                    }) {
                        HStack {
                            let isPlaying = soundManager.currentlyPlaying == sound
                            
                            // Left Icon
                            Image(systemName: isPlaying ? "speaker.wave.2.fill" : "music.note")
                                .foregroundColor(isPlaying ? .green : .yellow)
                                .frame(width: 25)
                            
                            // Filename
                            Text(sound)
                                .fontWeight(isPlaying ? .bold : .regular)
                                .foregroundColor(isPlaying ? .green : .primary)
                            
                            Spacer()
                            
                            // Play/Pause Icon
                            Image(systemName: isPlaying ? "pause.circle.fill" : "play.circle.fill")
                                .resizable()
                                .frame(width: 24, height: 24)
                                .foregroundColor(isPlaying ? .green : .yellow)
                        }
                        .padding(.vertical, 4)
                    }
                }
            }
            .navigationTitle("Sounds")
            .listStyle(InsetGroupedListStyle())
            .refreshable {
                soundManager.listSounds()
            }
        }
    }
}
