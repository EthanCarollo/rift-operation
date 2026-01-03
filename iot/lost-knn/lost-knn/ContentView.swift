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
    @StateObject private var wsManager = WebSocketManager()
    
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
            // Tab 1: Flower (Scanner)
            ScannerView(cameraManager: cameraManager, knnService: KNNService, wsManager: wsManager)
                .tabItem {
                    Label("Flower", systemImage: "leaf.fill")
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
            // Tab 4: Network
            WebSocketView(wsManager: wsManager)
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
