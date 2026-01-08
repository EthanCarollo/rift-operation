//
//  WebSocketView.swift
//  battle-mlx-cam
//
//  Modern iOS26 style network view
//

import SwiftUI

struct WebSocketView: View {
    @ObservedObject var wsManager: WebSocketManager
    
    var body: some View {
        ZStack {
            // Gradient background
            LinearGradient(
                colors: [Color(white: 0.05), Color(white: 0.1)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            VStack(spacing: 20) {
                // Header
                HStack {
                    Label("Network", systemImage: "network")
                        .font(.largeTitle.bold())
                        .foregroundStyle(.white)
                    
                    Spacer()
                    
                    // Status Badge
                    HStack(spacing: 8) {
                        Circle()
                            .fill(wsManager.isConnected ? .green : .red)
                            .frame(width: 10, height: 10)
                        Text(wsManager.isConnected ? "Connected" : "Disconnected")
                            .font(.subheadline.bold())
                            .foregroundStyle(wsManager.isConnected ? .green : .red)
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
                    .background(.ultraThinMaterial)
                    .clipShape(Capsule())
                }
                .padding(.horizontal)
                
                // Server Info Card
                GlassCard {
                    VStack(spacing: 16) {
                        ServerInfoRow(icon: "server.rack", label: "Server", value: "server.riftoperation.ethan-folio.fr")
                        Divider().background(.white.opacity(0.1))
                        ServerInfoRow(icon: "point.3.connected.trianglepath.dotted", label: "Path", value: "/ws")
                        Divider().background(.white.opacity(0.1))
                        ServerInfoRow(icon: "laptopcomputer", label: "Device", value: "battle-camera-mac")
                        Divider().background(.white.opacity(0.1))
                        ServerInfoRow(icon: "gamecontroller.fill", label: "Battle State", value: wsManager.battleState.uppercased())
                    }
                }
                .padding(.horizontal)
                
                // Controls
                HStack(spacing: 12) {
                    Button(action: { wsManager.connect() }) {
                        Label("Connect", systemImage: "link")
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.green)
                    .disabled(wsManager.isConnected)
                    
                    Button(action: { wsManager.disconnect() }) {
                        Label("Disconnect", systemImage: "link.badge.plus")
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.red)
                    .disabled(!wsManager.isConnected)
                }
                .padding(.horizontal)
                
                // Logs
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Label("Live Logs", systemImage: "list.bullet.rectangle")
                            .font(.headline)
                            .foregroundStyle(.secondary)
                        
                        Spacer()
                        
                        if !wsManager.messages.isEmpty {
                            Button(action: { wsManager.messages.removeAll() }) {
                                Image(systemName: "trash")
                                    .foregroundStyle(.secondary)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.horizontal)
                    
                    ScrollView {
                        LazyVStack(spacing: 8) {
                            ForEach(wsManager.messages, id: \.self) { msg in
                                LogRowModern(message: msg)
                            }
                        }
                        .padding(.horizontal)
                    }
                }
                .frame(maxHeight: .infinity)
            }
            .padding(.vertical)
        }
    }
}

// MARK: - Components

struct ServerInfoRow: View {
    let icon: String
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundStyle(.secondary)
                .frame(width: 24)
            
            Text(label)
                .foregroundStyle(.secondary)
            
            Spacer()
            
            Text(value)
                .font(.system(.callout, design: .monospaced))
                .foregroundStyle(.white)
        }
    }
}

struct LogRowModern: View {
    let message: String
    
    var isSending: Bool {
        message.contains("Sending") || message.contains("📤")
    }
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            // Icon
            Image(systemName: isSending ? "arrow.up.circle.fill" : "arrow.down.circle.fill")
                .foregroundStyle(isSending ? .blue : .orange)
                .font(.title3)
            
            VStack(alignment: .leading, spacing: 4) {
                // Timestamp
                if let time = extractTime(from: message) {
                    Text(time)
                        .font(.caption2)
                        .foregroundStyle(.tertiary)
                }
                
                // Content
                Text(extractContent(from: message))
                    .font(.system(.caption, design: .monospaced))
                    .foregroundStyle(.secondary)
                    .lineLimit(3)
            }
            
            Spacer()
        }
        .padding(12)
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .overlay {
            RoundedRectangle(cornerRadius: 12)
                .strokeBorder(
                    isSending ? Color.blue.opacity(0.3) : Color.orange.opacity(0.3),
                    lineWidth: 1
                )
        }
    }
    
    func extractTime(from msg: String) -> String? {
        if let start = msg.firstIndex(of: "["),
           let end = msg.firstIndex(of: "]") {
            return String(msg[msg.index(after: start)..<end])
        }
        return nil
    }
    
    func extractContent(from msg: String) -> String {
        if let idx = msg.firstIndex(of: "]") {
            return String(msg[msg.index(after: idx)...]).trimmingCharacters(in: .whitespaces)
        }
        return msg
    }
}
