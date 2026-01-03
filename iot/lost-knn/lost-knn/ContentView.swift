//
//  ContentView.swift
//  lost-knn
//
//  Created by Tom Boullay on 03/01/2025
//

import SwiftUI

struct ContentView: View {
    @StateObject private var cameraManager = CameraManager()
    @StateObject private var KNNService = KNNServiceClass()
    @State private var selectedTab = 0
    
    init() {
        let appearance = UITabBarAppearance()
        appearance.configureWithOpaqueBackground()
        appearance.backgroundColor = UIColor.black
        UITabBar.appearance().standardAppearance = appearance
        UITabBar.appearance().scrollEdgeAppearance = appearance
    }
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Tab 1: Scanner (Default)
            ScannerView(cameraManager: cameraManager, knnService: KNNService)
                .tabItem {
                    Label("Scanner", systemImage: "eye.circle.fill")
                }
                .tag(0)
            // Tab 2: Training
            TrainingView(cameraManager: cameraManager, knnService: KNNService)
                .tabItem {
                    Label("Training", systemImage: "brain.head.profile")
                }
                .tag(1)
            // Tab 3: Sounds
            SoundView()
                .tabItem {
                    Label("Sounds", systemImage: "music.note.list")
                }
                .tag(2)
            // Tab 4: WebSocket
            WebSocketView()
                .tabItem {
                    Label("Network", systemImage: "network")
                }
                .tag(3)
        }
        .accentColor(.yellow)
        .preferredColorScheme(.dark)
        .onAppear {
            cameraManager.start()
        }
    }
}

typealias KNNServiceClass = KNNService
