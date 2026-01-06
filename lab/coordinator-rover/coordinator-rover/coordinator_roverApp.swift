//
//  coordinator_roverApp.swift
//  coordinator-rover
//
//  Created by Tom Boullay on 06/01/2026.
//

import SwiftUI

@main
struct coordinator_roverApp: App {
    @StateObject private var wsManager = WebSocketManager()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(wsManager)
        }
    }
}
