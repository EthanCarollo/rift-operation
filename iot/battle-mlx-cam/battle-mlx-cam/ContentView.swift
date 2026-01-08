//
//  ContentView.swift
//  battle-mlx-cam
//
//  Main view with tab navigation
//

import SwiftUI

struct ContentView: View {
    @StateObject private var cameraManager = CameraManager()
    @StateObject private var wsManager = WebSocketManager()
    
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Tab 1: Camera
            CameraView(cameraManager: cameraManager, wsManager: wsManager)
                .tabItem {
                    Label("Camera", systemImage: "camera.fill")
                }
                .tag(0)
            
            // Tab 2: Network
            WebSocketView(wsManager: wsManager)
                .tabItem {
                    Label("Network", systemImage: "network")
                }
                .tag(1)
        }
        .preferredColorScheme(.dark)
        .onAppear {
            wsManager.connect()
        }
    }
}

#Preview {
    ContentView()
}
