//
//  SoundView.swift
//  lost-knn
//
//  Created by Tom Boullay on 03/01/2025
//

import SwiftUI

struct SoundView: View {
    @StateObject private var soundManager = SoundManager()
    
    var body: some View {
        NavigationView {
            List {
                ForEach(soundManager.availableSounds, id: \.self) { sound in
                    Button(action: {
                        soundManager.playSound(named: sound)
                    }) {
                        HStack {
                            Image(systemName: "music.note")
                                .foregroundColor(.yellow)
                            Text(sound)
                                .foregroundColor(.primary)
                            Spacer()
                            Image(systemName: "play.circle.fill")
                                .foregroundColor(.yellow)
                        }
                        .padding(.vertical, 8)
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
