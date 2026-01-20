//
//  ContentView.swift
//  operator-rover
//
//  Created by Tom Boullay on 06/01/2026.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        RobotView()
    }
}

#Preview {
    ContentView()
        .environmentObject(WebSocketManager())
}
