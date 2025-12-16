//
//  ContentView.swift
//  swift-sphero-rover
//
//  Created by Tom Boullay on 16/12/2025.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            Tab("Robot", systemImage: "robotic.vacuum") {
                RobotView()
            }
            
            Tab("WebSocket", systemImage: "wifi") {
                WebsocketView()
            }
        }
    }
}

#Preview {
    ContentView()
}
