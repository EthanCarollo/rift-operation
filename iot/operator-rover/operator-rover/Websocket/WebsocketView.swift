//
//  WebsocketView.swift
//  operator-rover
//
//  Created by Tom Boullay on 06/01/2026.
//

import SwiftUI

struct WebsocketView: View {
    @EnvironmentObject var wsManager: WebSocketManager
    
    var body: some View {
        let statusColor: Color = {
            switch wsManager.connectionStatus {
            case .connected: return .green
            case .connecting: return .yellow
            case .disconnected: return .red
            }
        }()

        ZStack {
            // Background
            Color.black.ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header
                HStack {
                    Text("NETLINK TERMINAL")
                        .font(.custom("Menlo-Bold", size: 16))
                        .foregroundColor(.green)
                    Spacer()
                    
                    HStack(spacing: 6) {
                        Circle()
                            .fill(statusColor)
                            .frame(width: 8, height: 8)
                            .shadow(color: statusColor, radius: 4)
                        
                        Text(wsManager.connectionStatus.rawValue)
                            .font(.custom("Menlo", size: 12))
                            .foregroundColor(statusColor)
                    }
                    .padding(6)
                    .background(Color.white.opacity(0.1))
                    .cornerRadius(4)
                }
                .padding()
                .background(Color.gray.opacity(0.15))
                
                // Server Selection
                Picker("Server", selection: $wsManager.serverMode) {
                   ForEach(ServerMode.allCases) { mode in
                       Text(mode.rawValue).tag(mode)
                   }
                }
                .pickerStyle(SegmentedPickerStyle())
                .padding(.horizontal)
                .padding(.vertical, 8)

                Divider().background(Color.gray)
                
                // Logs
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(alignment: .leading, spacing: 4) {
                            ForEach(wsManager.logs) { log in
                                Text(log.text)
                                    .font(.custom("Menlo", size: 12))
                                    .foregroundColor(.white.opacity(0.9))
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                    .padding(.horizontal)
                                    .id(log.id)
                            }
                        }
                        .padding(.vertical)
                    }
                    .onChange(of: wsManager.logs) { oldValue, newValue in
                        if let first = newValue.first {
                           // withAnimation {
                                proxy.scrollTo(first, anchor: .top)
                           // }
                        }
                    }
                }
                
                Divider().background(Color.gray)
                
                // Controls
                HStack {
                    Button(action: {
                        wsManager.connect()
                    }) {
                        Text("RECONNECT")
                            .font(.caption.bold())
                            .padding(8)
                            .background(Color.blue.opacity(0.3))
                            .foregroundColor(.blue)
                            .cornerRadius(4)
                    }
                    
                    Button(action: {
                        wsManager.disconnect()
                    }) {
                        Text("DISCONNECT")
                            .font(.caption.bold())
                            .padding(8)
                            .background(Color.red.opacity(0.3))
                            .foregroundColor(.red)
                            .cornerRadius(4)
                    }
                    
                    Spacer()
                }
                .padding()
                .background(Color.gray.opacity(0.1))
            }
        }
    }
}

#Preview {
    WebsocketView()
        .environmentObject(WebSocketManager())
}
