//
//  scenography_monitorApp.swift
//  scenography-monitor
//
//  Created by eth on 21/12/2025.
//

import SwiftUI

@main
struct scenography_monitorApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .onAppear {
                    // Ensure managers are alive
                    _ = WebSocketManager.shared
                    _ = SoundTrigger.shared
                }
        }
    }
}
