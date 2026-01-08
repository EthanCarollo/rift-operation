//
//  ContentView.swift
//  battle-mlx-cam
//
//  Main view with modern tab navigation
//

import SwiftUI

struct ContentView: View {
    @StateObject private var cameraManager = CameraManager()
    @StateObject private var wsManager = WebSocketManager()
    
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            CameraView(cameraManager: cameraManager, wsManager: wsManager)
                .tabItem {
                    Label("Camera", systemImage: "camera.fill")
                }
                .tag(0)
            
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
