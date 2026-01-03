//
//  WebSocketView.swift
//  lost-knn
//
//  Created by Tom Boullay on 03/01/2025
//

import SwiftUI

struct WebSocketView: View {
    @StateObject private var wsManager = WebSocketManager()
    
    var body: some View {
        ZStack {
            Color.black.edgesIgnoringSafeArea(.all)
            VStack(spacing: 20) {
                // Header
                Text("Network Status")
                    .font(.custom("AvenirNext-Bold", size: 30))
                    .foregroundColor(.white)
                    .padding(.top, 50)
                // Status Indicators
                HStack(spacing: 40) {
                    StatusIndicator(label: "WebSocket", isActive: wsManager.isConnected)
                }
                // Connection Info
                VStack(alignment: .leading, spacing: 5) {
                    Text("Server: ws://server.riftoperation.ethan-folio.fr")
                    Text("Path: /ws")
                }
                .font(.caption)
                .foregroundColor(.gray)
                .padding()
                .background(Color.white.opacity(0.1))
                .cornerRadius(10)
                // Controls
                HStack {
                    Button("Connect") {
                        wsManager.connect()
                    }
                    .padding()
                    .background(Color.green)
                    .foregroundColor(.white)
                    .cornerRadius(10)
                    .disabled(wsManager.isConnected)
                    .opacity(wsManager.isConnected ? 0.5 : 1)
                    
                    Button("Disconnect") {
                        wsManager.disconnect()
                    }
                    .padding()
                    .background(Color.red)
                    .foregroundColor(.white)
                    .cornerRadius(10)
                    .disabled(!wsManager.isConnected)
                    .opacity(!wsManager.isConnected ? 0.5 : 1)
                }
                // Log
                VStack(alignment: .leading) {
                    Text("Logs")
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding(.bottom, 5)
                    ScrollView {
                        LazyVStack(alignment: .leading, spacing: 8) {
                            ForEach(wsManager.messages, id: \.self) { msg in
                                Text(msg)
                                    .font(.system(.caption, design: .monospaced))
                                    .foregroundColor(.white.opacity(0.8))
                            }
                        }
                    }
                }
                .padding()
                .background(Color.white.opacity(0.05))
                .cornerRadius(15)
                .padding()
                
                Spacer()
            }
        }
        .onAppear {
            wsManager.connect()
        }
        .onDisappear {
            wsManager.disconnect()
        }
    }
}

struct StatusIndicator: View {
    let label: String
    let isActive: Bool
    
    var body: some View {
        VStack(spacing: 10) {
            Circle()
                .fill(isActive ? Color.green : Color.red)
                .frame(width: 20, height: 20)
                .shadow(color: isActive ? .green : .red, radius: 5)
            
            Text(label)
                .font(.subheadline)
                .foregroundColor(.white)
        }
    }
}
