//
//  ContentView.swift
//  operator-rover
//
//  Created by Tom Boullay on 06/01/2026.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            Tab("Robot", systemImage: "robotic.vacuum") {
                RobotView()
            }
            Tab ("Websocket", systemImage: "wifi") {
                WebsocketView()
            }
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(WebSocketManager())
}
