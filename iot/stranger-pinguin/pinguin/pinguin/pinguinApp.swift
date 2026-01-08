//
//  pinguinApp.swift
//  pinguin
//
//  Created by eth on 17/12/2025.
//

import SwiftUI

@main
struct pinguinApp: App {
    @State private var selectedServerMode: ServerMode? = nil
    
    var body: some Scene {
        WindowGroup {
            if let mode = selectedServerMode {
                ContentView(initialServerMode: mode)
                    .transition(.opacity)
            } else {
                ServerSelectionView(selectedMode: $selectedServerMode)
                    .transition(.opacity)
            }
        }
    }
}

