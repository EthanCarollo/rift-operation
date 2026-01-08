//
//  WebSocketView.swift
//  battle-mlx-cam
//
//  Network status and logs view
//

import SwiftUI

struct WebSocketView: View {
    @ObservedObject var wsManager: WebSocketManager
    
    var body: some View {
        ZStack {
            Color.black.edgesIgnoringSafeArea(.all)
            
            VStack(spacing: 0) {
                // Header
                HStack {
                    Text("Network")
                        .font(.system(size: 34, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                    Spacer()
                    StatusBadge(isConnected: wsManager.isConnected)
                }
                .padding(.horizontal)
                .padding(.top, 20)
                .padding(.bottom, 20)
                
                // Server Info
                VStack(alignment: .leading, spacing: 12) {
                    InfoRow(icon: "server.rack", title: "Server", value: "server.riftoperation.ethan-folio.fr")
                    Divider().background(Color.white.opacity(0.1))
                    InfoRow(icon: "network", title: "Path", value: "/ws")
                    Divider().background(Color.white.opacity(0.1))
                    InfoRow(icon: "laptopcomputer", title: "Device ID", value: "battle-camera-mac")
                    Divider().background(Color.white.opacity(0.1))
                    InfoRow(icon: "gamecontroller", title: "Battle State", value: wsManager.battleState.uppercased())
                }
                .padding()
                .background(Color(white: 0.1))
                .cornerRadius(16)
                .padding(.horizontal)
                .padding(.bottom, 20)
                
                // Controls
                HStack(spacing: 15) {
                    ActionButton(title: "Connect", icon: "link", color: .green, isDisabled: wsManager.isConnected) {
                        wsManager.connect()
                    }
                    ActionButton(title: "Disconnect", icon: "link.badge.plus", color: .red, isDisabled: !wsManager.isConnected) {
                        wsManager.disconnect()
                    }
                }
                .padding(.horizontal)
                .padding(.bottom, 20)
                
                // Logs
                VStack(alignment: .leading) {
                    HStack {
                        Text("Live Logs")
                            .font(.headline)
                            .foregroundColor(.gray)
                        Spacer()
                        if !wsManager.messages.isEmpty {
                            Button(action: { wsManager.messages.removeAll() }) {
                                Image(systemName: "trash")
                                    .foregroundColor(.gray)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.horizontal)
                    .padding(.bottom, 10)
                    
                    ScrollView {
                        LazyVStack(spacing: 12) {
                            ForEach(wsManager.messages, id: \.self) { msg in
                                LogRow(message: msg)
                            }
                        }
                        .padding(.horizontal)
                        .padding(.bottom, 20)
                    }
                }
            }
        }
    }
}

// MARK: - Components

struct StatusBadge: View {
    let isConnected: Bool
    
    var body: some View {
        HStack(spacing: 6) {
            Circle()
                .fill(isConnected ? Color.green : Color.red)
                .frame(width: 8, height: 8)
            Text(isConnected ? "Connected" : "Disconnected")
                .font(.subheadline.bold())
                .foregroundColor(isConnected ? .green : .red)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 6)
        .background(Color(white: 0.1))
        .clipShape(Capsule())
    }
}

struct InfoRow: View {
    let icon: String
    let title: String
    let value: String
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.gray)
                .frame(width: 24)
            Text(title)
                .foregroundColor(.gray)
            Spacer()
            Text(value)
                .font(.system(.callout, design: .monospaced))
                .foregroundColor(.white)
        }
    }
}

struct ActionButton: View {
    let title: String
    let icon: String
    let color: Color
    let isDisabled: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                Text(title)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(isDisabled ? Color(white: 0.15) : color)
            .foregroundColor(isDisabled ? .gray : .white)
            .cornerRadius(12)
        }
        .disabled(isDisabled)
        .buttonStyle(.plain)
    }
}

struct LogRow: View {
    let message: String
    
    var isSending: Bool {
        message.contains("Sending")
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(isSending ? "OUTGOING" : "INCOMING")
                    .font(.caption2.bold())
                    .foregroundColor(isSending ? .blue : .orange)
                    .padding(.horizontal, 6)
                    .padding(.vertical, 2)
                    .background((isSending ? Color.blue : Color.orange).opacity(0.2))
                    .cornerRadius(4)
                
                Spacer()
                
                if let idx = message.firstIndex(of: "]"), let start = message.firstIndex(of: "[") {
                    Text(message[message.index(after: start)..<idx])
                        .font(.caption2)
                        .foregroundColor(.gray)
                }
            }
            
            Text(extractContent(from: message))
                .font(.system(.caption, design: .monospaced))
                .foregroundColor(.white.opacity(0.9))
                .lineLimit(nil)
        }
        .padding(12)
        .background(Color(white: 0.1))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(isSending ? Color.blue.opacity(0.3) : Color.orange.opacity(0.3), lineWidth: 1)
        )
    }
    
    func extractContent(from msg: String) -> String {
        if let idx = msg.firstIndex(of: "]") {
            return String(msg[msg.index(after: idx)...]).trimmingCharacters(in: .whitespaces)
        }
        return msg
    }
}
